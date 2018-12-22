import peewee as p

db = p.SqliteDatabase('linkedin.db')


class Profile(p.Model):
    name = p.CharField(null=True)
    username = p.CharField(null=True)
    description = p.TextField(null=True)
    location = p.CharField(null=True)
    current_job = p.CharField(null=True)
    last_school = p.CharField(null=True)
    connections_number = p.IntegerField(null=True)
    skills_number = p.IntegerField(null=True)

    class Meta:
        database = db

class Skills(p.Model):
    skill_name = p.CharField()

    class Meta:
        database = db

class HasSkill(p.Model):
    user = p.ForeignKeyField(Profile)
    skill = p.ForeignKeyField(Skills)

    class Meta:
        database = db

class School(p.Model):
    name = p.CharField()

    class Meta:
        database = db

class Studied(p.Model):
    user = p.ForeignKeyField(Profile)
    school = p.ForeignKeyField(School)
    title = p.TextField(null=True)
    date = p.CharField(null=True)

    class Meta:
        database = db

class Organisation(p.Model):
    name = p.CharField()

    class Meta:
        database = db

class HasExperience(p.Model):
    user = p.ForeignKeyField(Profile)
    organisation = p.ForeignKeyField(Organisation)
    title = p.TextField(null=True)
    date = p.CharField(null=True)
    location = p.CharField(null=True)
    duration = p.CharField(null=True)

    class Meta:
        database = db

class Association(p.Model):
    name = p.CharField()

    class Meta:
        database = db

class VolunteeredAt(p.Model):
    user = p.ForeignKeyField(Profile)
    association = p.ForeignKeyField(Association)
    title = p.TextField(null=True)
    date = p.CharField(null=True)

    class Meta:
        database = db



if __name__ == "__main__":
    db.connect()
    db.create_tables([Profile, Skills, HasSkill, School, Studied, Organisation, HasExperience, Association, VolunteeredAt])
    db.close()