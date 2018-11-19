# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20180912_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_method',
            field=models.SmallIntegerField(verbose_name='支付方式', default=3, choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')]),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='total_price',
            field=models.DecimalField(verbose_name='商品总价', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='transit_price',
            field=models.DecimalField(verbose_name='订单运费', max_digits=10, decimal_places=2),
        ),
    ]
