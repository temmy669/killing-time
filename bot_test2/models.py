import time
import uuid
import os

from django.db import models


def uuid7():
    """Generate a UUID version 7 (time-ordered)."""
    # UUID v7: 48-bit Unix timestamp ms + random bits
    timestamp_ms = int(time.time() * 1000)
    ts_hex = f'{timestamp_ms:012x}'          # 48 bits = 12 hex chars
    rand_bits = os.urandom(10).hex()         # 80 random bits = 20 hex chars

    # Layout: xxxxxxxx-xxxx-7xxx-yxxx-xxxxxxxxxxxx
    part1 = ts_hex[:8]
    part2 = ts_hex[8:12]
    part3 = '7' + rand_bits[:3]
    part4 = format((int(rand_bits[3:5], 16) & 0x3F | 0x80), '02x') + rand_bits[5:7]
    part5 = rand_bits[7:19]

    return str(uuid.UUID(f'{part1}-{part2}-{part3}-{part4}-{part5}'))


class Profile(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid7, editable=False)
    name = models.CharField(max_length=255, unique=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    gender_probability = models.FloatField(null=True, blank=True)
    sample_size = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    age_group = models.CharField(max_length=20, null=True, blank=True)
    country_id = models.CharField(max_length=10, null=True, blank=True)
    country_probability = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f'{self.name} ({self.id})'