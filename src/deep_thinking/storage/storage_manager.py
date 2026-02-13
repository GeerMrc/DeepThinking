"""
存储管理器模块

提供思考会话的统一存储管理接口。
功能:
- 会话CRUD操作
- 索引管理
- 备份恢复
"""

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from deep_thinking.models.thinking_session import ThinkingSession
from deep_thinking.models.thought import Thought
from deep_thinking.storage.json_file_store import JsonFileStore

logger = logging.getLogger(__name__)


class StorageManager:
    """
    存储管理器

    管理思考会话的持久化存储，提供统一的CRUD接口。

    Attributes:
        data_dir: 数据存储目录
        store: JSON文件存储实例
        index_path: 索引文件路径
    """

    def __init__(self, data_dir: str | Path):
        """
        初始化存储管理器

        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # 创建JSON文件存储实例
        self.store = JsonFileStore(
            self.sessions_dir,
            backup_dir=self.data_dir / ".backups" / "sessions",
            enable_backup=True,
        )

        # 索引文件路径
        self.index_path = self.data_dir / "sessions" / ".index.json"

        # 初始化索引
        self._init_index()

    def _init_index(self) -> None:
        """初始化索引文件"""
        if not self.index_path.exists():
            self._write_index({})

    def _read_index(self) -> dict[str, Any]:
        """读取索引"""
        if not self.index_path.exists():
            return {}

        try:
            import json

            with open(self.index_path, encoding="utf-8") as f:
                return cast(dict[str, Any], json.load(f))
        except Exception as e:
            logger.error(f"读取索引失败: {e}")
            return {}

    def _write_index(self, index: dict[str, Any]) -> None:
        """写入索引"""
        try:
            import json

            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"写入索引失败: {e}")

    def _update_index_entry(self, session_id: str, name: str, status: str, updated_at: str) -> None:
        """更新索引条目"""
        index = self._read_index()
        index[session_id] = {
            "name": name,
            "status": status,
            "updated_at": updated_at,
        }
        self._write_index(index)

    def _remove_index_entry(self, session_id: str) -> None:
        """移除索引条目"""
        index = self._read_index()
        if session_id in index:
            del index[session_id]
            self._write_index(index)

    def create_session(
        self,
        name: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> ThinkingSession:
        """
        创建新会话

        Args:
            name: 会话名称
            description: 会话描述
            metadata: 元数据
            session_id: 会话ID（可选，不提供则自动生成UUID）

        Returns:
            创建的会话对象
        """
        if session_id is not None:
            session = ThinkingSession(
                name=name,
                description=description,
                metadata=metadata or {},
                session_id=session_id,
            )
        else:
            session = ThinkingSession(
                name=name,
                description=description,
                metadata=metadata or {},
            )

        # 保存会话
        self._save_session(session)

        # 更新索引
        self._update_index_entry(
            session.session_id,
            session.name,
            session.status,
            session.updated_at.isoformat(),
        )

        logger.info(f"创建会话: {session.session_id}")
        return session

    def get_session(self, session_id: str) -> ThinkingSession | None:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象，如果不存在则返回None
        """
        data = self.store.read(session_id)
        if data is None:
            return None

        # 重建思考步骤对象
        thoughts = []
        for thought_data in data.get("thoughts", []):
            thoughts.append(Thought(**thought_data))

        # 重建会话对象
        session_data = data.copy()
        session_data["thoughts"] = thoughts
        session = ThinkingSession(**session_data)

        return session

    def update_session(self, session: ThinkingSession) -> bool:
        """
        更新会话

        Args:
            session: 会话对象

        Returns:
            是否成功更新
        """
        # 检查会话是否存在
        if not self.store.exists(session.session_id):
            return False

        # 保存会话
        self._save_session(session)

        # 更新索引
        self._update_index_entry(
            session.session_id,
            session.name,
            session.status,
            session.updated_at.isoformat(),
        )

        logger.debug(f"更新会话: {session.session_id}")
        return True

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功删除
        """
        # 删除会话文件
        result = self.store.delete(session_id)

        if result:
            # 移除索引条目
            self._remove_index_entry(session_id)
            logger.info(f"删除会话: {session_id}")

        return result

    def list_sessions(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """
        列出会话

        Args:
            status: 过滤状态（active/completed/archived）
            limit: 最大返回数量

        Returns:
            会话摘要列表
        """
        sessions = []

        # 从索引读取
        index = self._read_index()

        for session_id, info in list(index.items())[:limit]:
            # 状态过滤
            if status and info.get("status") != status:
                continue

            # 获取完整会话数据
            session = self.get_session(session_id)
            if session:
                sessions.append(session.get_summary())

        # 按更新时间排序
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        return sessions

    def add_thought(self, session_id: str, thought: Thought) -> bool:
        """
        添加思考步骤到会话

        Args:
            session_id: 会话ID
            thought: 思考步骤

        Returns:
            是否成功添加
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        session.add_thought(thought)
        return self.update_session(session)

    def update_thought(self, session_id: str, thought: Thought) -> bool:
        """
        更新会话中的思考步骤

        Args:
            session_id: 会话ID
            thought: 思考步骤（根据 thought_number 匹配）

        Returns:
            是否成功更新
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        # 查找并更新思考步骤
        for i, existing_thought in enumerate(session.thoughts):
            if existing_thought.thought_number == thought.thought_number:
                session.thoughts[i] = thought
                return self.update_session(session)

        # 如果没找到，添加新的思考步骤
        session.add_thought(thought)
        return self.update_session(session)

    def get_latest_thought(self, session_id: str) -> Thought | None:
        """
        获取会话中最后一个思考步骤

        Args:
            session_id: 会话ID

        Returns:
            最后一个思考步骤，如果不存在则返回None
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        return session.get_latest_thought()

    def create_backup(self, backup_name: str | None = None) -> str | None:
        """
        创建完整备份

        Args:
            backup_name: 备份名称（默认使用时间戳）

        Returns:
            备份目录路径
        """
        if backup_name is None:
            backup_name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        backup_dir = self.data_dir / "backups" / backup_name

        try:
            # 备份会话目录
            if self.sessions_dir.exists():
                shutil.copytree(self.sessions_dir, backup_dir / "sessions")

            # 备份索引
            if self.index_path.exists():
                shutil.copy2(self.index_path, backup_dir / "index.json")

            logger.info(f"创建备份: {backup_dir}")
            return str(backup_dir)

        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return None

    def restore_backup(self, backup_name: str) -> bool:
        """
        从备份恢复

        Args:
            backup_name: 备份名称

        Returns:
            是否成功恢复
        """
        backup_dir = self.data_dir / "backups" / backup_name

        if not backup_dir.exists():
            logger.error(f"备份不存在: {backup_name}")
            return False

        try:
            # 恢复会话
            sessions_backup = backup_dir / "sessions"
            if sessions_backup.exists():
                if self.sessions_dir.exists():
                    shutil.rmtree(self.sessions_dir)
                shutil.copytree(sessions_backup, self.sessions_dir)

            # 恢复索引
            index_backup = backup_dir / "index.json"
            if index_backup.exists():
                shutil.copy2(index_backup, self.index_path)

            logger.info(f"从备份恢复: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def list_backups(self) -> list[dict[str, Any]]:
        """
        列出所有备份

        Returns:
            备份列表
        """
        backups: list[dict[str, Any]] = []
        backups_dir = self.data_dir / "backups"

        if not backups_dir.exists():
            return backups

        for backup_path in backups_dir.iterdir():
            if backup_path.is_dir():
                stat = backup_path.stat()
                backups.append(
                    {
                        "name": backup_path.name,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "size": stat.st_size,
                    }
                )

        # 按创建时间排序
        backups.sort(key=lambda x: x["created_at"], reverse=True)

        return backups

    def _save_session(self, session: ThinkingSession) -> None:
        """保存会话到文件"""
        data = session.to_dict()

        # 转换思考步骤为可序列化格式
        data["thoughts"] = [thought.to_dict() for thought in session.thoughts]

        # 使用JSON文件存储写入
        self.store.write(session.session_id, data)

    def get_stats(self) -> dict[str, Any]:
        """
        获取存储统计信息

        Returns:
            统计信息字典
        """
        index = self._read_index()

        # 统计各状态的会话数量
        status_counts = {"active": 0, "completed": 0, "archived": 0}
        for info in index.values():
            status = info.get("status", "active")
            if status in status_counts:
                status_counts[status] += 1

        # 统计总思考步骤数
        total_thoughts = 0
        for session_id in index:
            session = self.get_session(session_id)
            if session:
                total_thoughts += session.thought_count()

        return {
            "total_sessions": len(index),
            "status_counts": status_counts,
            "total_thoughts": total_thoughts,
            "data_dir": str(self.data_dir),
        }
