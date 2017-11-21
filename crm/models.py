from django.db import models


class Customer(models.Model):
    """客户信息表"""
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    qq_name = models.CharField(max_length=32)
    phone = models.CharField(max_length=64, blank=True, null=True)
    # 从哪个渠道了解的
    source_choices = (
        (0, '转介绍'),
        (1, 'QQ群'),
        (2, '官网'),
        (3, '百度推广'),
        (4, '51CTO'),
        (5, '知乎'),
        (6, '市场')
    )
    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.CharField(max_length=64, verbose_name="转介绍人QQ", blank=True, null=True)
    consult_course = models.ForeignKey("Course", verbose_name="咨询的课程")
    content = models.TextField(verbose_name="咨询的内容")
    tags = models.ManyToManyField("Tag", blank=True)
    status_choices = (
        (0, "已报名"),
        (1, "未报名")
    )
    status = models.SmallIntegerField(choices=status_choices, default=1)
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问")
    memo = models.TextField(verbose_name="备注", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq


class Tag(models.Model):
    """标签表"""
    name = models.CharField(unique=True, max_length=32)

    def __str__(self):
        return self.name


class CustomerFollowUp(models.Model):
    """客户跟进表"""
    customer = models.ForeignKey("Customer")
    consultant = models.ForeignKey("UserProfile", verbose_name="跟进人")
    content = models.TextField(verbose_name="跟进的内容")
    intention_choices = (
        (0, "2周内报名"),
        (1, "1个月内报名"),
        (2, "近期无报名计划"),
        (3, "已在其它机构报名"),
        (4, "已报名"),
        (5, "已拉黑")
    )
    intention = models.SmallIntegerField(choices=intention_choices, verbose_name="报名意向")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s : %s>" % (self.customer.qq, self.intention)


class Course(models.Model):
    """课程表"""
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期(月)")
    outline = models.TextField(verbose_name="课程大纲")

    def __str__(self):
        return self.name


class Branch(models.Model):
    """校区"""
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """班级表"""
    branch = models.ForeignKey("Branch", verbose_name="分校")
    course = models.ForeignKey("Course")
    class_type_choices = (
        (0, "面授(脱产)"),
        (1, "面授(周末"),
        (2, "网络班")
    )
    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name="上课类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateTimeField(verbose_name="开班日期")
    end_date = models.DateTimeField(verbose_name="结业日期", blank=True, null=True)

    def __str__(self):
        return "%s %s %s" % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course', 'semester')


class CourseRecord(models.Model):
    """上课记录表"""
    from_class = models.ForeignKey('ClassList', verbose_name="班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节(天)")
    teacher = models.ForeignKey("UserProfile")
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_content = models.TextField(verbose_name="作业内容")
    outline = models.TextField(verbose_name="本节课程大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')


class StudyRecord(models.Model):
    """学习记录表"""
    student = models.ForeignKey("Enrollment")
    course_record = models.ForeignKey("CourseRecord")
    attendance_choices = (
        (0, "已签到"),
        (1, "迟到"),
        (2, "缺勤"),
        (3, "早退")
    )
    attendance = models.SmallIntegerField(default=0, verbose_name="出勤记录")
    score_choices = (
        (100, "A+"),
        (90, "A"),
        (85, "B+"),
        (80, "B"),
        (75, "B-"),
        (70, "C+"),
        (60, "C"),
        (40, "C-"),
        (-50, "D"),
        (-100, "COPY"),
        (0, "N/A")
    )
    score = models.SmallIntegerField(choices=score_choices, default=0, verbose_name="成绩")
    memo = models.TextField(verbose_name="备注", blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.student, self.course_record, self.score)

    class Meta:
        unique_together = ('student', 'course_record')


class Enrollment(models.Model):
    """学生报名后的信息表"""
    customer = models.ForeignKey("Customer")
    enrolled_class = models.ForeignKey("ClassList", verbose_name="所报班级")
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问")
    contract_agreed = models.BooleanField(default=False, verbose_name="学员已同意条款")
    contract_approved = models.BooleanField(default=False, verbose_name="已审核")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ('customer', 'enrolled_class')


class Payment(models.Model):
    """缴费记录"""
    customer = models.ForeignKey("Customer")
    course = models.ForeignKey('Course', verbose_name="所报课程")
    amount = models.PositiveSmallIntegerField(verbose_name="数额", default=500)
    consultant = models.ForeignKey('UserProfile', verbose_name="课程顾问")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.customer, self.amount)


class UserProfile(models.Model):
    """员工账号表"""
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField('Role', blank=True)

    def __str__(self):
        return self.name


class Admin(models.Model):
    """管理员账号"""
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField("Menu", blank=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    """左侧菜单"""
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name
