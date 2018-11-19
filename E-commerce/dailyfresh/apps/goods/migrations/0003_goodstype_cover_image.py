# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_auto_20180920_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodstype',
            name='cover_image',
            field=models.ImageField(verbose_name='商品类型封面图', default=1, upload_to='type'),
            preserve_default=False,
        ),
    ]
