import pytest
from faker import Faker
from sqlalchemy import delete, insert, select, update

from db import Session
from models import Student

faker = Faker(["ja-JP"])


def test_select():
    """生徒の一覧を出力する

    ref: https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
    ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-orm-entities-and-attributes
    ref: https://docs.sqlalchemy.org/en/20/core/selectable.html
    """  # noqa
    with Session() as session:
        stmt = select(Student)
        result = session.execute(stmt)
        students = result.all()
        print(f"### students[{students}]")
        for (student,) in students:
            print(f"### student id[{student.id}] name[{student.name}]")


def test_insert():
    """生徒を追加する

    ref: https://docs.sqlalchemy.org/en/20/tutorial/data_insert.html
    ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-bulk-insert-statements
    ref: https://docs.sqlalchemy.org/en/20/core/dml.html#sqlalchemy.sql.expression.insert
    """  # noqa
    with Session() as session:
        stmt = insert(Student).values(
            name=faker.name(),
            gender=faker.pyint(min_value=1, max_value=2),
            address=faker.address(),
            score=faker.pyint(min_value=0, max_value=100),
        )
        session.execute(stmt)
        session.commit()


def test_insert_with_orm():
    """生徒を追加する(ORM 使用)

    ref: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#inserting-rows-using-the-orm-unit-of-work-pattern
    """  # noqa
    with Session() as session:
        stmt = insert(Student).values(
            name=faker.name(),
            gender=faker.pyint(min_value=1, max_value=2),
            address=faker.address(),
            score=faker.pyint(min_value=0, max_value=100),
        )
        session.execute(stmt)
        session.commit()


def test_update():
    """生徒の名前を更新する

    ref: https://docs.sqlalchemy.org/en/20/tutorial/data_update.html#the-update-sql-expression-construct
    ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-update-and-delete-with-custom-where-criteria
    ref: https://docs.sqlalchemy.org/en/20/core/dml.html#sqlalchemy.sql.expression.update
    """  # noqa
    with Session() as session:
        stmt = (
            update(Student)
            .values(
                name=f"UPDATE S{faker.name()}",
            )
            .where(Student.id == 1)
        )
        session.execute(stmt)
        session.commit()


def test_update_with_orm():
    """生徒の名前を更新する(ORM 使用)

    ref: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#updating-orm-objects-using-the-unit-of-work-pattern
    """  # noqa
    with Session() as session:
        stmt = select(Student).where(Student.id == 1)
        result = session.execute(stmt)
        student = result.scalar()
        student.name = f"UPDATE S{faker.name()}"
        session.commit()


def test_delete():
    """生徒を削除する

    ref: https://docs.sqlalchemy.org/en/20/tutorial/data_update.html#the-delete-sql-expression-construct
    ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-update-and-delete-with-custom-where-criteria
    ref: https://docs.sqlalchemy.org/en/20/core/dml.html#sqlalchemy.sql.expression.delete
    """  # noqa
    with Session() as session:
        stmt = delete(Student).where(Student.id == 1)
        session.execute(stmt)
        session.commit()


@pytest.mark.xfail(reason="エラーとなる。cascade に関する確認が必要")
def test_delete_with_orm():
    """生徒を削除する(ORM 使用)

    ref: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#deleting-orm-objects-using-the-unit-of-work-pattern
    ref: https://docs.sqlalchemy.org/en/20/orm/cascades.html#using-foreign-key-on-delete-cascade-with-orm-relationships
    """  # noqa
    with Session() as session:
        stmt = select(Student).where(Student.id == 2)
        result = session.execute(stmt)
        student = result.scalar()
        session.delete(student)
        session.commit()
