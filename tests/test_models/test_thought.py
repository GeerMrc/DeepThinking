"""
思考步骤模型单元测试
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from deep_thinking.models.thought import Thought, ThoughtCreate, ThoughtUpdate


class TestThought:
    """Thought模型测试"""

    def test_create_regular_thought(self):
        """测试创建常规思考"""
        thought = Thought(thought_number=1, content="这是一个常规思考")
        assert thought.thought_number == 1
        assert thought.content == "这是一个常规思考"
        assert thought.type == "regular"
        assert thought.is_revision is False
        assert thought.is_regular_thought() is True
        assert thought.is_revision_thought() is False
        assert thought.is_branch_thought() is False
        assert thought.get_display_type() == "💭"

    def test_create_revision_thought(self):
        """测试创建修订思考"""
        thought = Thought(
            thought_number=2,
            content="这是修订后的思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        assert thought.type == "revision"
        assert thought.is_revision is True
        assert thought.revises_thought == 1
        assert thought.is_revision_thought() is True
        assert thought.get_display_type() == "🔄"

    def test_create_branch_thought(self):
        """测试创建分支思考"""
        thought = Thought(
            thought_number=3,
            content="这是分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="alt-1",
        )
        assert thought.type == "branch"
        assert thought.branch_from_thought == 1
        assert thought.branch_id == "alt-1"
        assert thought.is_branch_thought() is True
        assert thought.get_display_type() == "🌿"

    def test_thought_number_validation(self):
        """测试思考编号验证"""
        with pytest.raises(ValidationError):
            Thought(thought_number=0, content="思考")  # 编号必须>=1

        with pytest.raises(ValidationError):
            Thought(thought_number=-1, content="思考")  # 编号必须>=1

    def test_content_validation(self):
        """测试思考内容验证"""
        with pytest.raises(ValidationError):
            Thought(thought_number=1, content="")  # 内容不能为空

        with pytest.raises(ValidationError):
            Thought(thought_number=1, content="x" * 10001)  # 内容不能超过10000字符

    def test_revision_requires_revises_thought(self):
        """测试修订思考必须指定revises_thought"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
            )
        assert "revises_thought" in str(exc_info.value)

    def test_revision_requires_is_revision_true(self):
        """测试修订思考类型需要is_revision=True"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=False,
                revises_thought=1,
            )
        assert "is_revision" in str(exc_info.value)

    def test_branch_requires_branch_from_thought(self):
        """测试分支思考必须指定branch_from_thought"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
            )
        assert "branch_from_thought" in str(exc_info.value)

    def test_branch_requires_branch_id(self):
        """测试分支思考必须指定branch_id"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
                branch_from_thought=1,
            )
        assert "branch_id" in str(exc_info.value)

    def test_revises_thought_must_be_less_than_current(self):
        """测试revises_thought必须小于当前thought_number"""
        with pytest.raises(ValidationError) as exc_info:
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
                revises_thought=2,  # 不能等于当前编号
            )
        assert "必须小于" in str(exc_info.value)

        with pytest.raises(ValidationError):
            Thought(
                thought_number=2,
                content="修订思考",
                type="revision",
                is_revision=True,
                revises_thought=3,  # 不能大于当前编号
            )

    def test_branch_from_thought_must_be_less_than_current(self):
        """测试branch_from_thought必须小于当前thought_number"""
        with pytest.raises(ValidationError):
            Thought(
                thought_number=2,
                content="分支思考",
                type="branch",
                branch_from_thought=2,
                branch_id="alt-1",
            )

    def test_timestamp_default(self):
        """测试时间戳默认值"""
        before = datetime.utcnow()
        thought = Thought(thought_number=1, content="思考")
        after = datetime.utcnow()

        assert thought.timestamp >= before
        assert thought.timestamp <= after

    def test_to_dict(self):
        """测试转换为字典"""
        thought = Thought(thought_number=1, content="测试思考", type="regular")
        data = thought.to_dict()

        assert data["thought_number"] == 1
        assert data["content"] == "测试思考"
        assert data["type"] == "regular"
        assert "timestamp" in data
        assert data["display_type"] == "💭"
        assert isinstance(data["timestamp"], str)


class TestThoughtCreate:
    """ThoughtCreate模型测试"""

    def test_to_thought(self):
        """测试转换为Thought模型"""
        create_data = ThoughtCreate(
            thought_number=1,
            content="新思考",
            type="regular",
        )
        thought = create_data.to_thought()

        assert isinstance(thought, Thought)
        assert thought.thought_number == 1
        assert thought.content == "新思考"
        assert thought.type == "regular"

    def test_create_revision(self):
        """测试创建修订思考输入"""
        create_data = ThoughtCreate(
            thought_number=2,
            content="修订思考",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        thought = create_data.to_thought()

        assert thought.type == "revision"
        assert thought.revises_thought == 1

    def test_create_branch(self):
        """测试创建分支思考输入"""
        create_data = ThoughtCreate(
            thought_number=2,
            content="分支思考",
            type="branch",
            branch_from_thought=1,
            branch_id="alt-1",
        )
        thought = create_data.to_thought()

        assert thought.type == "branch"
        assert thought.branch_id == "alt-1"


class TestThoughtUpdate:
    """ThoughtUpdate模型测试"""

    def test_update_content_only(self):
        """测试只更新内容"""
        update_data = ThoughtUpdate(content="更新后的内容")
        assert update_data.content == "更新后的内容"
        assert update_data.type is None

    def test_update_multiple_fields(self):
        """测试更新多个字段"""
        update_data = ThoughtUpdate(
            content="新内容",
            type="revision",
            is_revision=True,
            revises_thought=1,
        )
        assert update_data.content == "新内容"
        assert update_data.type == "revision"
        assert update_data.revises_thought == 1

    def test_all_fields_optional(self):
        """测试所有字段都是可选的"""
        update_data = ThoughtUpdate()
        assert update_data.content is None
        assert update_data.type is None
        assert update_data.is_revision is None
