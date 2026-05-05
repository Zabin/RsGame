"""
narrative.py — Dialog trees and narrative system for Bunny Garden Adventure.

Enables branching story with dialog nodes, choices, and conditional scenes
without requiring code changes for new stories or dialog.
"""


class DialogNode:
    """A single block of dialog text."""

    def __init__(self, node_id, text, speaker="", audio_cue=""):
        """
        Args:
            node_id: Unique identifier for this node
            text: Dialog text (displayed to player)
            speaker: Character name speaking (optional)
            audio_cue: Name of sound effect or music cue (optional)
        """
        self.node_id = node_id
        self.text = text
        self.speaker = speaker
        self.audio_cue = audio_cue
        self.choices = {}  # label -> next_node_id

    def add_choice(self, label, next_node_id):
        """Add a player choice that leads to another node."""
        self.choices[label] = next_node_id
        return self

    def has_choices(self):
        """Return True if this node has player choices."""
        return len(self.choices) > 0

    def __repr__(self):
        choice_count = len(self.choices)
        return f"DialogNode({self.node_id} {self.speaker} {choice_count} choices)"


class Scene:
    """A named collection of connected dialog nodes (e.g., an encounter or cutscene)."""

    def __init__(self, scene_id, name, start_node_id):
        """
        Args:
            scene_id: Unique identifier
            name: Human-readable name
            start_node_id: ID of the first node in this scene
        """
        self.scene_id = scene_id
        self.name = name
        self.start_node_id = start_node_id
        self.nodes = {}  # node_id -> DialogNode

    def add_node(self, node):
        """Add a dialog node to this scene."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists in scene")
        self.nodes[node.node_id] = node
        return node

    def get_node(self, node_id):
        """Retrieve a dialog node by ID."""
        return self.nodes.get(node_id)

    def __repr__(self):
        return f"Scene({self.scene_id} {self.name} {len(self.nodes)} nodes)"


class DialogTree:
    """A complete narrative tree with multiple scenes and story branches."""

    def __init__(self, name, version="1.0"):
        """
        Args:
            name: Story name (e.g., "Main Campaign", "Side Quest")
            version: Story version for tracking changes
        """
        self.name = name
        self.version = version
        self.scenes = {}  # scene_id -> Scene
        self.current_scene = None
        self.current_node = None

    def add_scene(self, scene):
        """Register a scene."""
        if scene.scene_id in self.scenes:
            raise ValueError(f"Scene {scene.scene_id} already registered")
        self.scenes[scene.scene_id] = scene
        return scene

    def get_scene(self, scene_id):
        """Retrieve a scene by ID."""
        return self.scenes.get(scene_id)

    def start_scene(self, scene_id):
        """Begin a scene, starting at its initial node."""
        scene = self.get_scene(scene_id)
        if scene is None:
            raise ValueError(f"Scene {scene_id} not found")
        self.current_scene = scene
        self.current_node = scene.get_node(scene.start_node_id)
        if self.current_node is None:
            raise ValueError(f"Start node {scene.start_node_id} not found in scene")
        return self.current_node

    def advance_node(self, choice_index=0):
        """
        Move to the next dialog node.

        Args:
            choice_index: Index or label of choice to take (0 for auto-advance)

        Returns:
            Next DialogNode, or None if scene ended
        """
        if self.current_node is None:
            return None

        if self.current_node.has_choices():
            # Multi-choice node
            choices_list = list(self.current_node.choices.items())

            if isinstance(choice_index, str):
                # Find by label
                next_node_id = None
                for label, next_id in choices_list:
                    if label == choice_index:
                        next_node_id = next_id
                        break
                if next_node_id is None:
                    return None
            else:
                # By index (1-based)
                if choice_index == 0 or choice_index > len(choices_list):
                    return None  # Player must choose
                next_node_id = choices_list[choice_index - 1][1]

            next_node = self.current_scene.get_node(next_node_id)
            if next_node is None:
                return None
            self.current_node = next_node
            return next_node
        else:
            # Auto-advance node
            # Look for next node (simple linear progression)
            # In practice, would link via choice with implicit "next"
            return None

    def get_current_node(self):
        """Get the current dialog node."""
        return self.current_node

    def encode(self):
        """Generate binary encoding of narrative tree for ROM."""
        data = bytearray()

        # Header: name length, version
        data.append(len(self.name))
        for c in self.name:
            data.append(ord(c) & 0xFF)
        data.append(len(self.version))
        for c in self.version:
            data.append(ord(c) & 0xFF)

        # Scene count
        data.append(len(self.scenes))

        # Scenes
        for scene in self.scenes.values():
            # Scene header
            data.append(len(scene.scene_id))
            for c in scene.scene_id:
                data.append(ord(c) & 0xFF)
            data.append(len(scene.name))
            for c in scene.name:
                data.append(ord(c) & 0xFF)
            data.append(len(scene.start_node_id))
            for c in scene.start_node_id:
                data.append(ord(c) & 0xFF)

            # Nodes in scene
            data.append(len(scene.nodes))
            for node in scene.nodes.values():
                # Node header
                data.append(len(node.node_id))
                for c in node.node_id:
                    data.append(ord(c) & 0xFF)
                data.append(len(node.text))
                for c in node.text[:255]:
                    data.append(ord(c) & 0xFF)
                data.append(len(node.speaker))
                for c in node.speaker:
                    data.append(ord(c) & 0xFF)

                # Choices
                data.append(len(node.choices))
                for label, next_id in node.choices.items():
                    data.append(len(label))
                    for c in label:
                        data.append(ord(c) & 0xFF)
                    data.append(len(next_id))
                    for c in next_id:
                        data.append(ord(c) & 0xFF)

        return bytes(data)

    def __repr__(self):
        return f"DialogTree({self.name} v{self.version} {len(self.scenes)} scenes)"


class StoryManager:
    """Manages all narrative content for the game."""

    def __init__(self):
        self.trees = {}  # tree_id -> DialogTree
        self.active_tree = None

    def register_tree(self, tree):
        """Register a narrative tree."""
        if tree.name in self.trees:
            raise ValueError(f"Tree '{tree.name}' already registered")
        self.trees[tree.name] = tree
        return tree

    def get_tree(self, name):
        """Retrieve a narrative tree."""
        return self.trees.get(name)

    def start_tree(self, name, scene_id):
        """Start playing a narrative tree from a specific scene."""
        tree = self.get_tree(name)
        if tree is None:
            raise ValueError(f"Tree '{name}' not found")
        self.active_tree = tree
        return tree.start_scene(scene_id)

    def advance(self, choice_index=0):
        """Advance current dialog."""
        if self.active_tree is None:
            return None
        return self.active_tree.advance_node(choice_index)

    def get_current_node(self):
        """Get current dialog node."""
        if self.active_tree is None:
            return None
        return self.active_tree.get_current_node()

    def list_trees(self):
        """List all registered narrative trees."""
        return list(self.trees.values())

    def __repr__(self):
        return f"StoryManager({len(self.trees)} trees)"


# Global story manager
manager = StoryManager()


def load_narrative_from_json(json_path):
    """Load narrative trees from JSON asset file."""
    import json
    from pathlib import Path

    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"Asset file not found: {json_path}")

    with open(json_file) as f:
        assets = json.load(f)

    # Load narrative trees
    if "narratives" in assets:
        for tree_name, tree_def in assets["narratives"].items():
            version = tree_def.get("version", "1.0")
            tree = DialogTree(tree_name, version=version)

            # Load scenes
            if "scenes" in tree_def:
                for scene_id, scene_def in tree_def["scenes"].items():
                    scene_name = scene_def.get("name", scene_id)
                    start_node = scene_def.get("start", None)

                    if start_node is None:
                        continue

                    scene = Scene(scene_id, scene_name, start_node)

                    # Load nodes in scene
                    if "nodes" in scene_def:
                        for node_id, node_def in scene_def["nodes"].items():
                            text = node_def.get("text", "")
                            speaker = node_def.get("speaker", "")
                            audio = node_def.get("audio", "")

                            node = DialogNode(node_id, text, speaker, audio)

                            # Load choices
                            if "choices" in node_def:
                                for choice in node_def["choices"]:
                                    label = choice.get("label", "")
                                    next_id = choice.get("next", "")
                                    if label and next_id:
                                        node.add_choice(label, next_id)

                            scene.add_node(node)

                    tree.add_scene(scene)

            manager.register_tree(tree)

    return manager
