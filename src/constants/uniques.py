from engine.scene_node import SceneNode
from inventory.inventory_node import InventoryNode

# Global active scene accessor.
ACTIVE_SCENE: SceneNode | None = None

# Global inventory accessor.
INVENTORY: InventoryNode = InventoryNode()