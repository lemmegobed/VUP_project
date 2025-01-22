# Generated by Django 5.1.3 on 2025-01-22 12:46

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "profile",
                    models.ImageField(
                        blank=True,
                        default="profiles/default_profile_image.png",
                        null=True,
                        upload_to="profiles/",
                    ),
                ),
                ("sex", models.CharField(max_length=10)),
                ("birthdate", models.DateField(blank=True, null=True)),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="เพิ่มคำอธิบายของคุณ",
                        max_length=30,
                        null=True,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_name", models.CharField(max_length=50)),
                ("event_title", models.CharField(max_length=100)),
                ("event_datetime", models.DateTimeField()),
                ("location", models.CharField(max_length=200)),
                ("category", models.CharField(max_length=100)),
                (
                    "province",
                    models.CharField(
                        choices=[
                            ("choose province", "เลือกจังหวัด"),
                            ("Bangkok", "Bangkok (กรุงเทพมหานคร)"),
                            ("Krabi", "Krabi (กระบี่)"),
                            ("Kanchanaburi", "Kanchanaburi (กาญจนบุรี)"),
                            ("Kalasin", "Kalasin (กาฬสินธุ์)"),
                            ("Kamphaeng Phet", "Kamphaeng Phet (กำแพงเพชร)"),
                            ("Khon Kaen", "Khon Kaen (ขอนแก่น)"),
                            ("Chanthaburi", "Chanthaburi (จันทบุรี)"),
                            ("Chachoengsao", "Chachoengsao (ฉะเชิงเทรา)"),
                            ("Chonburi", "Chonburi (ชลบุรี)"),
                            ("Chainat", "Chainat (ชัยนาท)"),
                            ("Chaiyaphum", "Chaiyaphum (ชัยภูมิ)"),
                            ("Chumphon", "Chumphon (ชุมพร)"),
                            ("Chiang Rai", "Chiang Rai (เชียงราย)"),
                            ("Chiang Mai", "Chiang Mai (เชียงใหม่)"),
                            ("Trang", "Trang (ตรัง)"),
                            ("Trat", "Trat (ตราด)"),
                            ("Tak", "Tak (ตาก)"),
                            ("Nakhon Nayok", "Nakhon Nayok (นครนายก)"),
                            ("Nakhon Pathom", "Nakhon Pathom (นครปฐม)"),
                            ("Nakhon Phanom", "Nakhon Phanom (นครพนม)"),
                            ("Nakhon Ratchasima", "Nakhon Ratchasima (นครราชสีมา)"),
                            (
                                "Nakhon Si Thammarat",
                                "Nakhon Si Thammarat (นครศรีธรรมราช)",
                            ),
                            ("Nan", "Nan (น่าน)"),
                            ("Nonthaburi", "Nonthaburi (นนทบุรี)"),
                            ("Narathiwat", "Narathiwat (นราธิวาส)"),
                            ("Phayao", "Phayao (พะเยา)"),
                            (
                                "Prachuap Khiri Khan",
                                "Prachuap Khiri Khan (ประจวบคีรีขันธ์)",
                            ),
                            ("Pattani", "Pattani (ปัตตานี)"),
                            (
                                "Phra Nakhon Si Ayutthaya",
                                "Phra Nakhon Si Ayutthaya (พระนครศรีอยุธยา)",
                            ),
                            ("Phang Nga", "Phang Nga (พังงา)"),
                            ("Phatthalung", "Phatthalung (พัทลุง)"),
                            ("Phichit", "Phichit (พิจิตร)"),
                            ("Phitsanulok", "Phitsanulok (พิษณุโลก)"),
                            ("Phetchaburi", "Phetchaburi (เพชรบุรี)"),
                            ("Phetchabun", "Phetchabun (เพชรบูรณ์)"),
                            ("Phrae", "Phrae (แพร่)"),
                            ("Phuket", "Phuket (ภูเก็ต)"),
                            ("Maha Sarakham", "Maha Sarakham (มหาสารคาม)"),
                            ("Mukdahan", "Mukdahan (มุกดาหาร)"),
                            ("Mae Hong Son", "Mae Hong Son (แม่ฮ่องสอน)"),
                            ("Yasothon", "Yasothon (ยโสธร)"),
                            ("Yala", "Yala (ยะลา)"),
                            ("Roi Et", "Roi Et (ร้อยเอ็ด)"),
                            ("Ranong", "Ranong (ระนอง)"),
                            ("Rayong", "Rayong (ระยอง)"),
                            ("Ratchaburi", "Ratchaburi (ราชบุรี)"),
                            ("Lopburi", "Lopburi (ลพบุรี)"),
                            ("Lampang", "Lampang (ลำปาง)"),
                            ("Lamphun", "Lamphun (ลำพูน)"),
                            ("Loei", "Loei (เลย)"),
                            ("Sisaket", "Sisaket (ศรีสะเกษ)"),
                            ("Sakon Nakhon", "Sakon Nakhon (สกลนคร)"),
                            ("Songkhla", "Songkhla (สงขลา)"),
                            ("Satun", "Satun (สตูล)"),
                            ("Samut Prakan", "Samut Prakan (สมุทรปราการ)"),
                            ("Samut Songkhram", "Samut Songkhram (สมุทรสงคราม)"),
                            ("Samut Sakhon", "Samut Sakhon (สมุทรสาคร)"),
                            ("Sa Kaeo", "Sa Kaeo (สระแก้ว)"),
                            ("Saraburi", "Saraburi (สระบุรี)"),
                            ("Sing Buri", "Sing Buri (สิงห์บุรี)"),
                            ("Sukhothai", "Sukhothai (สุโขทัย)"),
                            ("Suphan Buri", "Suphan Buri (สุพรรณบุรี)"),
                            ("Surat Thani", "Surat Thani (สุราษฎร์ธานี)"),
                            ("Surin", "Surin (สุรินทร์)"),
                            ("Nong Khai", "Nong Khai (หนองคาย)"),
                            ("Nong Bua Lamphu", "Nong Bua Lamphu (หนองบัวลำภู)"),
                            ("Ang Thong", "Ang Thong (อ่างทอง)"),
                            ("Udon Thani", "Udon Thani (อุดรธานี)"),
                            ("Uttaradit", "Uttaradit (อุตรดิตถ์)"),
                            ("Uthai Thani", "Uthai Thani (อุทัยธานี)"),
                            ("Ubon Ratchathani", "Ubon Ratchathani (อุบลราชธานี)"),
                        ],
                        max_length=100,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("max_participants", models.PositiveIntegerField(default=0)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ChatRoom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("users", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                (
                    "event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="myapp.event"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "chatroom",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="myapp.chatroom",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("request", "คำขอเข้าร่วมกิจกรรม"),
                            ("response", "ตอบกลับคำขอ"),
                            ("other", "อื่น ๆ"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "related_event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="myapp.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("ความผิดพลาดของระบบ", "ความผิดพลาดของระบบ"),
                            ("พฤติกรรมไม่เหมาะสม", "พฤติกรรมไม่เหมาะสม"),
                            ("Other", "อื่นๆ"),
                        ],
                        max_length=50,
                        verbose_name="ประเภทการรายงาน",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="คำอธิบาย"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="เวลาที่รายงาน"
                    ),
                ),
                (
                    "is_warned",
                    models.CharField(
                        choices=[
                            ("รอดำเนินการ", "รอดำเนินการ"),
                            ("เตือน", "เตือน"),
                            ("ปฏิเสธการรายงาน", "ปฏิเสธการรายงาน"),
                        ],
                        default="รอดำเนินการ",
                        max_length=15,
                        verbose_name="สถานะการแจ้งเตือน",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reported_events",
                        to="myapp.event",
                        verbose_name="อีเว้นที่ถูกรายงาน",
                    ),
                ),
                (
                    "event_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events_owned",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="เจ้าของอีเว้น",
                    ),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports_made",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้รายงาน",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=150)),
                (
                    "profile",
                    models.ImageField(
                        blank=True,
                        default="profiles/default_profile_image.png",
                        null=True,
                        upload_to="profiles/",
                    ),
                ),
                ("sex", models.CharField(blank=True, max_length=10, null=True)),
                ("birthdate", models.DateField(blank=True, null=True)),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="เพิ่มคำอธิบายของคุณ",
                        max_length=30,
                        null=True,
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Event_Request",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("request_time", models.DateTimeField(auto_now_add=True)),
                (
                    "response_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requests",
                        to="myapp.event",
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["event", "receiver", "response_status"],
                        name="myapp_event_event_i_ce261c_idx",
                    )
                ],
            },
        ),
    ]
