"""ORM 用のモデル

ref: https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html
"""  # noqa

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import INTEGER, Boolean, Enum, ForeignKey, String, func
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 循環インポート対策
# ref: https://github.com/sqlalchemy/sqlalchemy/discussions/9576
# ref: https://mypy.readthedocs.io/en/stable/runtime_troubles.html#import-cycles
if TYPE_CHECKING:
    from models_club import Club, StudentClub


class Base(DeclarativeBase):
    pass


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Student(Base):
    """
    - Email に対しては one-to-many
    - StudentClazz に対しては one-to-one
    - StudentClub に対しては one-to-many

    ref: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    ref: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    ref: https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship
    ref: https://docs.sqlalchemy.org/en/20/orm/collection_api.html#customizing-collection-access
    ref: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-python-enum-or-pep-586-literal-types-in-the-type-map

    NOTE: `relationship()` の `back_populates` では、リレーション先に存在する attribute を指定する。存在しない場合はエラーとなる
    """  # noqa

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # NOTE: Enum 型にすると、テーブルには定義値(key)の文字列を insert する。
    #       この場合は MALE/FEMALE の Enum 型となる。
    #       DDL 的には `/`gender/` enum('MALE','FEMALE') NOT NULL,`
    # gender: Mapped[Gender] = mapped_column(Enum(Gender))
    # NOTE: 既存のテーブルが存在し varchar に対して後付けで Enum 型にしたい場合は
    #       `native_enum=False` を付与する。
    #       enum クラスに存在しないメンバ変数が含まれた場合は LookupError の
    #       例外を発行する。
    # gender: Mapped[Gender] = mapped_column(Enum(Gender, native_enum=False))
    # NOTE: enum の key ではなく value を適用したい場合は values_callable を使う。
    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            name="gender_enum",
            native_enum=False,
            length=10,
            values_callable=lambda x: [i.value for i in x],
        )
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[int] = mapped_column(INTEGER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    emails: Mapped[list["Email"]] = relationship(back_populates="student")
    # Classic Style: emails = relationship("Email", collection_class=set, back_populates="student")  # noqa

    clazz: Mapped["StudentClazz"] = relationship()
    # NOTE: Imperative な場合に one-to-one 制約を付与する場合は
    #       親側の relationship に `uselist=False` を付与する
    # Classic Style: clazz = relationship("Clazz", uselist=False, back_populates="student")  # noqa

    clubs: Mapped[list["StudentClub"]] = relationship(back_populates="student")

    # 楽観的ロックの検証用。システム的に updated_at を更新するため version_id_generator は False となる
    __mapper_args__ = {"version_id_col": updated_at, "version_id_generator": False}


class Email(Base):
    __tablename__ = "emails"

    # TODO: mail 用の型とかある？
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    student_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("students.id", ondelete="CASCADE")
    )

    # NOTE: 複合主キー
    # ref: https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#mapper-configuration-options-with-declarative  # noqa
    __mapper_args__ = {"primary_key": [email, student_id]}

    # 検証用に back_populates は指定していない
    student: Mapped["Student"] = relationship()


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # primaryjoin については `04_relationships_tips.py::test_primaryjoin` を参照
    club: Mapped["Club"] = relationship(
        primaryjoin="Teacher.id==Club.teacher_id", foreign_keys=id
    )


class Clazz(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class StudentClazz(Base):
    """
    - Student に対して one-to-one
    - Clazz に対して one-to-one

    ref: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#declarative-table-configuration
    ref: https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.UniqueConstraint
    """  # noqa

    __tablename__ = "student_clazz"

    student_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    class_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("classes.id", ondelete="RESTRICT")
    )

    student: Mapped["Student"] = relationship(back_populates="clazz")
    clazz: Mapped["Clazz"] = relationship()


class TeacherClazz(Base):
    __tablename__ = "teacher_clazz"

    teacher_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("teachers.id", ondelete="RESTRICT")
    )
    class_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("classes.id", ondelete="CASCADE")
    )

    __mapper_args__ = {"primary_key": [teacher_id, class_id]}
