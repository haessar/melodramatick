from django.conf import settings
from django.db import migrations


def create_award_levels(apps, schema_editor):
    AwardLevel = apps.get_model("top_list", "AwardLevel")
    AwardLevel.objects.get_or_create(rank=1, level="platinum", color_hex=settings.AWARD_LEVEL_PLATINUM_HEX)
    AwardLevel.objects.get_or_create(rank=2, level="gold", color_hex=settings.AWARD_LEVEL_GOLD_HEX)
    AwardLevel.objects.get_or_create(rank=3, level="silver", color_hex=settings.AWARD_LEVEL_SILVER_HEX)
    AwardLevel.objects.get_or_create(rank=4, level="bronze", color_hex=settings.AWARD_LEVEL_BRONZE_HEX)


def delete_award_levels(apps, schema_editor):
    AwardLevel = apps.get_model("top_list", "AwardLevel")
    AwardLevel.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('top_list', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(code=create_award_levels, reverse_code=delete_award_levels),
    ]
