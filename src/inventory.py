from abc import ABC, abstractmethod

DATA_FILE = "items.json"

# ==========================================================
# Observer Pattern: Notifier Interface & Implementations
# ==========================================================
class BaseNotifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class ConsoleNotifier(BaseNotifier):
    def send(self, message: str) -> None:
        print(f"\n[ALERT - Console] {message}")

class LogNotifier(BaseNotifier):
    def send(self, message: str) -> None:
        print(f"\n[LOG FILE MOCK] Written to audit log: {message}")

# ==========================================================
# Factory Pattern: NotifierFactory
# ==========================================================
class NotifierFactory:
    @staticmethod
    def create(channel: str) -> BaseNotifier:
        channel_lower = channel.strip().lower()
        if channel_lower == "console":
            return ConsoleNotifier()
        elif channel_lower == "log":
            return LogNotifier()
        else:
            raise ValueError(f"Unknown notification channel: {channel}")

# ==========================================================
# Core Domain & InventoryService (DIP + Observer Subject)
# ==========================================================
class InventoryService:
    def __init__(self, observers: list[BaseNotifier] | None = None):
        self.observers: list[BaseNotifier] = observers if observers is not None else []
        self.items: list[dict] = []

    def attach(self, observer: BaseNotifier) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def low_stock_items(self, threshold: int) -> list:
        if threshold < 0:
            return []
        matching_items = [
            item for item in getattr(self, "items", [])
            if item.get("stock", 0) <= threshold
        ]
        return sorted(matching_items, key=lambda x: x.get("name", ""))