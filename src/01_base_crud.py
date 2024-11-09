from typing import Sequence, Tuple

from faker import Faker
from sqlalchemy import delete, false, insert, select, update

# モデルを最初に使おうとするときには、依存するマッピングをすべて取り込むために、依存するモジュールすべてを最初にインポートする必要がある。
# 循環インポートの場合などでは使うモデルのリレーション先が TYPE_CHECKING によりロードされないケースがありえるため明示的にロードする必要がある。
# (今回の場合では Student に依存する StudentClub のロードが必要なので models_club を import した)
# ref: https://github.com/sqlalchemy/sqlalchemy/discussions/10334#discussioncomment-6970773  # noqa
import models_club  # noqa
from db import Session
from models import Student

faker = Faker(["ja-JP"])


def test_select_all():
    """生徒の一覧を出力する

    ref: https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
    ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-orm-entities-and-attributes
    ref: https://docs.sqlalchemy.org/en/20/core/selectable.html
    """  # noqa
    with Session() as session:
        stmt = select(Student)
        result = session.execute(stmt)
        students: Sequence[Tuple[Student]] = result.all()
        print(f"### students[{students}]")
        for (student,) in students:
            print(
                f"### student id[{student.id}] name[{student.name}] gender[{student.gender}] is_active[{student.is_active}]"
            )


def test_select_scalar():
    """単一の生徒情報を出力する"""
    with Session() as session:
        stmt = select(Student).where(Student.id == 1, Student.is_active == false())
        # TODO: where に `foo is False` のような書き方は、動くが期待しない結果になるため注意！
        # ref: https://dev.classmethod.jp/articles/tips-for-boolean-type-filtering-with-flake8-in-sqlalchemy/
        # stmt = select(Student).where(Student.id == 1, Student.is_active is False)
        student = session.execute(stmt).scalar()
        if student:
            print(
                f"### student id[{student.id}] name[{student.name}] gender[{student.gender}] is_active[{student.is_active}]"
            )
        else:
            print("### student is None")


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
