from django.conf import settings
from django.db import migrations


def create_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site = Site.objects.create(id=settings.SITE_ID, domain="testtick.local", name="testtick.local")
    site.save()


def delete_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site = Site.objects.get(id=settings.SITE_ID)
    site.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('testtick', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(code=create_site, reverse_code=delete_site),
    ]
