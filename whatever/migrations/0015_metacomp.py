# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RunningScore'
        db.create_table('whatever_runningscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['whatever.CustomUser'])),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('goaldiff', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('edited_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['whatever.Competition'])),
        ))
        db.send_create_signal('whatever', ['RunningScore'])

        # Adding M2M table for field positions on 'RunningScore'
        db.create_table('whatever_runningscore_positions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('runningscore', models.ForeignKey(orm['whatever.runningscore'], null=False)),
            ('position', models.ForeignKey(orm['whatever.position'], null=False))
        ))
        db.create_unique('whatever_runningscore_positions', ['runningscore_id', 'position_id'])

        # Adding field 'Prediction.included_in_meta_competition'
        db.add_column('whatever_prediction', 'included_in_meta_competition', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Removing M2M table for field leagues on 'customuser'
        db.delete_table('whatever_customuser_leagues')


    def backwards(self, orm):
        
        # Deleting model 'RunningScore'
        db.delete_table('whatever_runningscore')

        # Removing M2M table for field positions on 'RunningScore'
        db.delete_table('whatever_runningscore_positions')

        # Deleting field 'Prediction.included_in_meta_competition'
        db.delete_column('whatever_prediction', 'included_in_meta_competition')

        # Adding M2M table for field leagues on 'customuser'
        db.create_table('whatever_customuser_leagues', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customuser', models.ForeignKey(orm['whatever.customuser'], null=False)),
            ('league', models.ForeignKey(orm['whatever.league'], null=False))
        ))
        db.create_unique('whatever_customuser_leagues', ['customuser_id', 'league_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'whatever.competition': {
            'Meta': {'object_name': 'Competition'},
            'close_date': ('django.db.models.fields.DateTimeField', [], {}),
            'competition_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'prize': ('django.db.models.fields.CharField', [], {'max_length': '180', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'teaser': ('django.db.models.fields.CharField', [], {'max_length': '180', 'null': 'True', 'blank': 'True'})
        },
        'whatever.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'can_email': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'current_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.League']", 'symmetrical': 'False', 'through': "orm['whatever.LeagueJoinStates']", 'blank': 'True'}),
            'login_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'supported_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Team']", 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'whatever.division': {
            'Meta': {'object_name': 'Division'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'whatever.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'whatever.emailupdatelines': {
            'Meta': {'object_name': 'EmailUpdateLines'},
            'email': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lines'", 'to': "orm['whatever.EmailMessage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.CharField', [], {'max_length': '180'})
        },
        'whatever.fixture': {
            'Meta': {'object_name': 'Fixture'},
            'away': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'away_fixtures'", 'to': "orm['whatever.Team']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'home': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'home_fixtures'", 'to': "orm['whatever.Team']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'whatever.league': {
            'Meta': {'object_name': 'League'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        },
        'whatever.leaguejoinstates': {
            'Meta': {'object_name': 'LeagueJoinStates'},
            'date_assigned': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.League']"}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"})
        },
        'whatever.leaguetable': {
            'Meta': {'object_name': 'LeagueTable'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Team']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.DateField', [], {})
        },
        'whatever.position': {
            'Meta': {'object_name': 'Position'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'whatever.prediction': {
            'Meta': {'object_name': 'Prediction'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Competition']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edited_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goaldiff': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_in_meta_competition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_used_goaldiff_table': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'predictions_for_goaldiff'", 'blank': 'True', 'null': 'True', 'to': "orm['whatever.LeagueTable']"}),
            'last_used_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.LeagueTable']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'needs_ordering': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'needs_update': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Position']", 'symmetrical': 'False'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Team']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"}),
            'year': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'whatever.registrationprofile': {
            'Meta': {'object_name': 'RegistrationProfile'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"})
        },
        'whatever.runningscore': {
            'Meta': {'object_name': 'RunningScore'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Competition']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edited_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goaldiff': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Position']", 'symmetrical': 'False'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"})
        },
        'whatever.team': {
            'Meta': {'object_name': 'Team'},
            'division': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Division']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        }
    }

    complete_apps = ['whatever']
