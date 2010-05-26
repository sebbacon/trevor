# -*- coding: utf-8 -*-
# python

# django
from django.core.urlresolvers import reverse
from django.core import mail

# app
from base import BaseTest
from base import PASSWORD
from whatever.models import CustomUser
from whatever.models import League
from whatever.models import RegistrationProfile
from whatever.models import LeagueJoinStates
from whatever.models import STATE_REJECTED, STATE_DECLINED
from whatever.models import STATE_APPLIED, STATE_INVITED
from utils import getCurrentPrediction

class LeagueTest(BaseTest):
    fixtures = ['test-data']
    def test_creation_form(self):
        self._login()
        url = reverse('add_league')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        post_data = {'name':'',
                     'form-0-email':'',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertContains(response,'This field is required.')
        post_data = {'name':'asdf1',
                     'form-0-email':'',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertContains(response, 'You must supply at least one email')

    def test_creation(self):
        self._login()
        url = reverse('add_league')
        post_data = {'name':'asdf1',
                     'form-0-email':'testie@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))
        # try doing the same again.  It shouldn't let us use the same name
        post_data = {'name':'asdf1',
                     'form-0-email':'testie@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertContains(response,
                            'A league called asdf1 already exists')

        # new guy should have got an email
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject,
                          "Invitation to join asdf1")

        # and they should exist as an invalid user
        testuser = CustomUser.objects\
                   .get(email='testie@mailinator.com')
        self.assertFalse(testuser.is_active)

        # and they should appear in my league
        league = League.objects.get(name='asdf1')
        self.assertEquals(league.owner, self.user)
        self.assertEquals(len(league.members_and_applicants()), 2)
        self.assertEquals(len(league.members()), 1)

    def test_apply(self):
        """When a user tries to create a new team, and invites someone
        they know who happens already to be in another team, we ask
        them if they want to join that other team instead.
        """
        # create a team as test user 1
        self._login()
        url = reverse('add_league')
        post_data = {'name':'asdf1',
                     'form-0-email':'testie@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        league1 = League.objects.get(name='asdf1')
        self.client.logout()
        
        # now try to create a team that invites test user 1 to join
        self.client.login(username=self.user2.username,
                          password=PASSWORD)
        
        post_data = {'name':'asdf2',
                     'form-0-email':self.user.email,
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        # no team should have been created 
        self.assertRaises(League.DoesNotExist,
                          League.objects.get,
                          name='asdf2')
        # the user is prompted if they'd like to join user 1's team
        could_join = response.context['could_join']
        self.assertEquals(list(could_join), [league1])
        # so we do so
        post_data = {'name':'asdf2',
                     'join_leagues':[could_join.pop().pk],
                     'form-0-email':'test@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))
        self.assertEquals(mail.outbox[-1].subject,
                          "Application to join asdf1")        
        # because we want to join someone else's team, make sure
        # we ignored the team this user originally wanted to create
        self.assertRaises(League.DoesNotExist,
                          League.objects.get,
                          name='asdf2')

        # now we've joined the team, if we go through the same process
        # again, we shouldn't be offered the team we just joined as a
        # possibility 
        post_data = {'name':'asdf2',
                     'form-0-email':self.user.email,
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertEquals(len(response.context['could_join']), 0)
        self.assertEquals(list(response.context['applied']),
                          [league1]) 
        # and the last action should still not have created a team
        self.assertRaises(League.DoesNotExist,
                          League.objects.get,
                          name='asdf2')

        # now we try again, but this time we really do want to create
        # a new team
        post_data = {'name':'asdf2',
                     'yes_really':'yup',
                     'foo':'bar',
                     'form-0-email':self.user.email,
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertEquals(League.objects.get(name='asdf2').name,
                          'asdf2') 


    def test_league_email_validate(self):
        """Check emails with trailing whitespace are cleaned up
        automatically
        
        """
        self._login()
        url = reverse('add_league')
        post_data = {'name':'asdf1',
                     'form-0-email':'testie1@mailinator.com ',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data)
        self.assertEquals(response.status_code, 302)

    def test_accept_twice(self):
        """If a user follows an 'accept' link twice from an email, we
        want to deal with the case where they didn't make a
        prediction.  So we want to allow accepting twice.

        """
        # create a team as test user 1 and invite testie1
        return 
        self._login()
        url = reverse('add_league')
        post_data = {'name':'asdf1',
                     'form-0-email':'testie1@mailinator.com',
                     'form-1-email': 'testie2@mailinator.com',
                     'form-2-email': self.user2.email,
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 3}
        response = self.client.post(url, post_data)
        league = League.objects.get(name='asdf1')
        user = CustomUser.objects.get(email='testie1@mailinator.com')
        self.assertFalse(bool(getCurrentPrediction(user)))
        self.assertEquals(len(league.members()), 1)
        self.assertFalse(user.is_active)
        self.client.logout()
        # this user accepts the invite; their account becomes active
        key = RegistrationProfile.objects.get(email='testie1@mailinator.com')\
              .activation_key
        confirm_url = reverse('accept_league_invite',
                              kwargs=dict(league=league.slug,
                                          key=key))
        response = self.client.get(confirm_url, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))

        # try to accept the invite again
        response = self.client.get(confirm_url, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))

    def test_join_workflow(self):
        """When users apply or are invited to join a league, they must
        go through a simple approve-type workflow before they're
        really in it.

        New users get to verify their account at the same time.
        """
        # create a team as test user 1 and invite testie1
        self._login()
        url = reverse('add_league')
        post_data = {'name':'asdf1',
                     'form-0-email':'testie1@mailinator.com',
                     'form-1-email': 'testie2@mailinator.com',
                     'form-2-email': self.user2.email,
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 3}
        response = self.client.post(url, post_data)
        league = League.objects.get(name='asdf1')
        user = CustomUser.objects.get(email='testie1@mailinator.com')
        self.assertFalse(bool(getCurrentPrediction(user)))
        self.assertEquals(len(league.members()), 1)
        self.assertFalse(user.is_active)
        self.client.logout()
        # this user accepts the invite; their account becomes active
        key = RegistrationProfile.objects.get(email='testie1@mailinator.com')\
              .activation_key
        confirm_url = reverse('accept_league_invite',
                              kwargs=dict(league=league.slug,
                                          key=key))
        response = self.client.get(confirm_url, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))
        league = League.objects.get(name='asdf1')
        self.assertEquals(len(league.members()), 2)
        user = CustomUser.objects.get(email='testie1@mailinator.com')
        self.assertTrue(user.is_active)

        # this user tries to accept an invite that's never been issued
        key = RegistrationProfile.objects.get(email=self.user3.email)\
              .activation_key
        confirm_url = reverse('accept_league_invite',
                              kwargs=dict(league=league.slug,
                                          key=key))
        response = self.client.get(confirm_url)
        self.assertContains(response, "Sorry")
        league = League.objects.get(name='asdf1')
        self.assertEquals(len(league.members()), 2)

        # and this user declines the invite
        key = RegistrationProfile.objects.get(email=self.user2.email)\
              .activation_key
        decline_url = reverse('decline_league_invite',
                              kwargs=dict(league=league.slug,
                                          key=key))
        response = self.client.get(decline_url, follow=True)
        self.assertRedirects(response, reverse('home'))
        league = League.objects.get(name='asdf1')
        self.assertEquals(len(league.members()), 2)
        declined = CustomUser.objects\
                   .filter(leaguejoinstates__state=STATE_DECLINED)
        self.assertEquals(len(declined.all()), 1)

        # now another user wants to join this team...
        self.client.logout()
        self.client.login(username=self.user3.username,
                          password=PASSWORD)

        key = RegistrationProfile.objects.get(email=self.user3.email)\
              .activation_key
        accept_url = reverse('approve_league_application',
                             kwargs=dict(email=self.user3.email,
                                         league=league.slug))

        # ...but you can't accept someone who's not applied
        response = self.client.get(accept_url)
        self.assertContains(response, "Sorry")
        post_data = {'name':'asdf2',
                     'join_leagues':[league.pk],
                     'form-0-email':'test@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        response = self.client.post(url, post_data, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))
        self.assertEquals(mail.outbox[-1].subject,
                          'Application to join asdf1')                          
        applied = CustomUser.objects\
                  .filter(leaguejoinstates__state=STATE_APPLIED)
        self.assertEquals(len(applied.all()), 1)

        # now try to join again; shouldn't be able to
        post_data = {'name':'asdf2',
                     'join_leagues':[league.pk],
                     'form-0-email':'test@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        self.assertRaises(LeagueJoinStates.InvalidStateTransition,
                          self.client.post,
                          url,
                          post_data)
        
        # now they've applied, we can accept them; but only if we're
        # logged in as the league owner
        response = self.client.get(accept_url)
        self.assertContains(response, "Sorry")
        self.client.logout()
        # try again as owner
        self._login()
        response = self.client.get(accept_url, follow=True)
        self.assertRedirects(response, reverse('make_prediction'))
        applied = CustomUser.objects\
                  .filter(leaguejoinstates__state=STATE_APPLIED)
        self.assertEquals(len(applied.all()), 0)
        league = League.objects.get(name='asdf1')
        self.assertEquals(len(league.members()), 3)

        # but we can reject people who are in our own team, too
        reject_url = reverse('reject_league_application',
                             kwargs=dict(email=self.user3.email,
                                         league=league.slug))        
        response = self.client.get(reject_url, follow=True)
        rejected = CustomUser.objects\
                   .filter(leaguejoinstates__state=STATE_REJECTED)
        self.assertEquals(len(rejected.all()), 1)
        league = League.objects.get(name='asdf1')
        self.assertEquals(len(league.members()), 2)

        # and now that person can no longer apply to join
        self.client.logout()
        self.client.login(username=self.user3.username,
                          password=PASSWORD)
        post_data = {'name':'asdf2',
                     'join_leagues':[league.pk],
                     'form-0-email':'test@mailinator.com',
                     'form-INITIAL_FORMS': 0,
                     'form-TOTAL_FORMS': 1}
        self.assertRaises(LeagueJoinStates.InvalidStateTransition,
                          self.client.post,
                          url,
                          post_data)        
        applied = CustomUser.objects\
                  .filter(leaguejoinstates__state=STATE_APPLIED)
        self.assertEquals(len(applied.all()), 0)
 
