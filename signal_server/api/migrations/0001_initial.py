# Generated by Django 2.2.4 on 2020-12-05 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identityKey', models.CharField(max_length=44)),
                ('registrationId', models.PositiveIntegerField()),
                ('address', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SignedPreKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyId', models.PositiveIntegerField()),
                ('publicKey', models.CharField(max_length=44)),
                ('signature', models.CharField(max_length=88)),
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Device')),
            ],
        ),
        migrations.CreateModel(
            name='PreKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyId', models.PositiveIntegerField()),
                ('publicKey', models.CharField(max_length=44)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Device')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=1000)),
                ('senderRegistrationId', models.PositiveIntegerField()),
                ('senderAddress', models.CharField(max_length=100)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='api.Device')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.AddConstraint(
            model_name='prekey',
            constraint=models.UniqueConstraint(fields=('device', 'keyId'), name='unique_keyId'),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('user', 'address')},
        ),
    ]
