
from south.db import db
from django.db import models
from whatever.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Prediction'
        db.create_table('whatever_prediction', (
            ('id', orm['whatever.Prediction:id']),
            ('name', orm['whatever.Prediction:name']),
            ('year', orm['whatever.Prediction:year']),
            ('user', orm['whatever.Prediction:user']),
            ('score', orm['whatever.Prediction:score']),
            ('goaldiff', orm['whatever.Prediction:goaldiff']),
            ('created_date', orm['whatever.Prediction:created_date']),
            ('last_used_table', orm['whatever.Prediction:last_used_table']),
        ))
        db.send_create_signal('whatever', ['Prediction'])
        
        # Adding model 'Team'
        db.create_table('whatever_team', (
            ('id', orm['whatever.Team:id']),
            ('name', orm['whatever.Team:name']),
            ('slug', orm['whatever.Team:slug']),
        ))
        db.send_create_signal('whatever', ['Team'])
        
        # Adding model 'Position'
        db.create_table('whatever_position', (
            ('id', orm['whatever.Position:id']),
            ('position', orm['whatever.Position:position']),
            ('date', orm['whatever.Position:date']),
        ))
        db.send_create_signal('whatever', ['Position'])
        
        # Adding model 'LeagueTable'
        db.create_table('whatever_leaguetable', (
            ('id', orm['whatever.LeagueTable:id']),
            ('name', orm['whatever.LeagueTable:name']),
            ('year', orm['whatever.LeagueTable:year']),
            ('added', orm['whatever.LeagueTable:added']),
        ))
        db.send_create_signal('whatever', ['LeagueTable'])
        
        # Adding model 'League'
        db.create_table('whatever_league', (
            ('id', orm['whatever.League:id']),
            ('name', orm['whatever.League:name']),
            ('slug', orm['whatever.League:slug']),
            ('date', orm['whatever.League:date']),
            ('owner', orm['whatever.League:owner']),
        ))
        db.send_create_signal('whatever', ['League'])
        
        # Adding model 'RegistrationProfile'
        db.create_table('whatever_registrationprofile', (
            ('id', orm['whatever.RegistrationProfile:id']),
            ('user', orm['whatever.RegistrationProfile:user']),
            ('email', orm['whatever.RegistrationProfile:email']),
            ('activation_key', orm['whatever.RegistrationProfile:activation_key']),
            ('activated', orm['whatever.RegistrationProfile:activated']),
        ))
        db.send_create_signal('whatever', ['RegistrationProfile'])
        
        # Adding model 'CustomUser'
        db.create_table('whatever_customuser', (
            ('user_ptr', orm['whatever.CustomUser:user_ptr']),
            ('postcode', orm['whatever.CustomUser:postcode']),
            ('can_email', orm['whatever.CustomUser:can_email']),
            ('current_score', orm['whatever.CustomUser:current_score']),
        ))
        db.send_create_signal('whatever', ['CustomUser'])
        
        # Adding model 'LeagueJoinStates'
        db.create_table('whatever_leaguejoinstates', (
            ('id', orm['whatever.LeagueJoinStates:id']),
            ('league', orm['whatever.LeagueJoinStates:league']),
            ('user', orm['whatever.LeagueJoinStates:user']),
            ('state', orm['whatever.LeagueJoinStates:state']),
            ('date_assigned', orm['whatever.LeagueJoinStates:date_assigned']),
        ))
        db.send_create_signal('whatever', ['LeagueJoinStates'])
        
        # Adding ManyToManyField 'Prediction.positions'
        db.create_table('whatever_prediction_positions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('prediction', models.ForeignKey(orm.Prediction, null=False)),
            ('position', models.ForeignKey(orm.Position, null=False))
        ))
        
        # Adding ManyToManyField 'LeagueTable.teams'
        db.create_table('whatever_leaguetable_teams', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('leaguetable', models.ForeignKey(orm.LeagueTable, null=False)),
            ('team', models.ForeignKey(orm.Team, null=False))
        ))
        
        # Adding ManyToManyField 'Prediction.teams'
        db.create_table('whatever_prediction_teams', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('prediction', models.ForeignKey(orm.Prediction, null=False)),
            ('team', models.ForeignKey(orm.Team, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Prediction'
        db.delete_table('whatever_prediction')
        
        # Deleting model 'Team'
        db.delete_table('whatever_team')
        
        # Deleting model 'Position'
        db.delete_table('whatever_position')
        
        # Deleting model 'LeagueTable'
        db.delete_table('whatever_leaguetable')
        
        # Deleting model 'League'
        db.delete_table('whatever_league')
        
        # Deleting model 'RegistrationProfile'
        db.delete_table('whatever_registrationprofile')
        
        # Deleting model 'CustomUser'
        db.delete_table('whatever_customuser')
        
        # Deleting model 'LeagueJoinStates'
        db.delete_table('whatever_leaguejoinstates')
        
        # Dropping ManyToManyField 'Prediction.positions'
        db.delete_table('whatever_prediction_positions')
        
        # Dropping ManyToManyField 'LeagueTable.teams'
        db.delete_table('whatever_leaguetable_teams')
        
        # Dropping ManyToManyField 'Prediction.teams'
        db.delete_table('whatever_prediction_teams')
        
    
    
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
        'whatever.customuser': {
            'can_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'current_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'leagues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['whatever.League']", 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
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
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goaldiff': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['whatever']
