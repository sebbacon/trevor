
from south.db import db
from django.db import models
from whatever.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Competition'
        db.create_table('whatever_competition', (
            ('id', orm['whatever.competition:id']),
            ('name', orm['whatever.competition:name']),
            ('start_date', orm['whatever.competition:start_date']),
            ('close_date', orm['whatever.competition:close_date']),
        ))
        db.send_create_signal('whatever', ['Competition'])
        
        prevcomp = orm.Competition.objects\
                   .create(name="Trevor's league 2008/09",
                           start_date=datetime.datetime(2008,10,1),
                           close_date=datetime.datetime(2009,9,15))
        comp = orm.Competition.objects\
               .create(name="Trevor's league 2009/10",
                       start_date=datetime.datetime(2009,10,1),
                       close_date=datetime.datetime(2010,5,31))
    
        # Adding field 'Prediction.last_used_goaldiff_table'
        db.add_column('whatever_prediction', 'last_used_goaldiff_table', orm['whatever.prediction:last_used_goaldiff_table'])
        foreign_key = orm['whatever.prediction:competition']
        foreign_key.default = comp.pk
        # Adding field 'Prediction.competition'
        db.add_column('whatever_prediction', 'competition', foreign_key)

        # set the league position for the prevcomp
        prevleague = orm.LeagueTable.objects.get(name__contains="2008")
        prevleague.competition = prevcomp
        prevleague.save()
    
    def backwards(self, orm):
        
        # Deleting model 'Competition'
        db.delete_table('whatever_competition')
        
        # Deleting field 'Prediction.last_used_goaldiff_table'
        db.delete_column('whatever_prediction', 'last_used_goaldiff_table_id')
        
        # Deleting field 'Prediction.competition'
        db.delete_column('whatever_prediction', 'competition_id')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'whatever.competition': {
            'close_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'whatever.customuser': {
            'can_email': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'current_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.League']", 'blank': 'True'}),
            'supported_team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Team']", 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'whatever.division': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'whatever.league': {
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        },
        'whatever.leaguejoinstates': {
            'date_assigned': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.League']"}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"})
        },
        'whatever.leaguetable': {
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Team']"}),
            'year': ('django.db.models.fields.DateField', [], {})
        },
        'whatever.position': {
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'whatever.prediction': {
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Competition']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goaldiff': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_used_goaldiff_table': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'predictions_for_goaldiff'", 'blank': 'True', 'null': 'True', 'to': "orm['whatever.LeagueTable']"}),
            'last_used_table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.LeagueTable']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'positions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Position']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"}),
            'year': ('django.db.models.fields.DateField', [], {})
        },
        'whatever.registrationprofile': {
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.CustomUser']"})
        },
        'whatever.team': {
            'division': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['whatever.Division']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['whatever']
