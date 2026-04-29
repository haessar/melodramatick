# Generated for the Melodramatick template validation app.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('work', '0010_alter_work_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testitem',
            fields=[
                ('work_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='work.work')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('work.work',),
        ),
    ]
