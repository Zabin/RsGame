"""Unit tests for narrative system (dialog trees, scenes, branching story).

Tests dialog nodes, narrative trees, and story asset loading from JSON.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestDialogNode:
    """Tests for DialogNode class."""

    def test_dialog_node_creation(self):
        """DialogNode can be created with text."""
        from narrative import DialogNode

        node = DialogNode("intro1", "Hello, adventurer!", speaker="Sage")
        assert node.node_id == "intro1"
        assert node.text == "Hello, adventurer!"
        assert node.speaker == "Sage"

    def test_dialog_node_add_choice(self):
        """Choices can be added to node."""
        from narrative import DialogNode

        node = DialogNode("choice1", "What do you do?")
        node.add_choice("Talk more", "talk1")
        node.add_choice("Leave", "end1")
        assert len(node.choices) == 2
        assert node.choices["Talk more"] == "talk1"

    def test_dialog_node_has_choices(self):
        """has_choices() returns True when choices exist."""
        from narrative import DialogNode

        node1 = DialogNode("n1", "Text")
        assert node1.has_choices() is False

        node1.add_choice("Yes", "next1")
        assert node1.has_choices() is True

    def test_dialog_node_add_choice_returns_self(self):
        """add_choice() returns self for chaining."""
        from narrative import DialogNode

        node = DialogNode("n1", "Text")
        result = node.add_choice("Yes", "n2")
        assert result is node

    def test_dialog_node_audio_cue(self):
        """Dialog node can have audio cue."""
        from narrative import DialogNode

        node = DialogNode("n1", "Thunder!", audio_cue="thunder_sound")
        assert node.audio_cue == "thunder_sound"

    def test_dialog_node_repr(self):
        """DialogNode repr shows ID, speaker, choice count."""
        from narrative import DialogNode

        node = DialogNode("choice1", "Pick one", speaker="Sage")
        node.add_choice("Yes", "next1")
        node.add_choice("No", "next2")
        repr_str = repr(node)
        assert "choice1" in repr_str
        assert "Sage" in repr_str
        assert "2 choices" in repr_str


class TestScene:
    """Tests for Scene class."""

    def test_scene_creation(self):
        """Scene can be created with ID and start node."""
        from narrative import Scene

        scene = Scene("garden_visit", "Visit Garden", "node_start")
        assert scene.scene_id == "garden_visit"
        assert scene.name == "Visit Garden"
        assert scene.start_node_id == "node_start"

    def test_scene_add_node(self):
        """Nodes can be added to scene."""
        from narrative import Scene, DialogNode

        scene = Scene("intro", "Intro", "n1")
        node = DialogNode("n1", "Welcome!")
        scene.add_node(node)
        assert "n1" in scene.nodes

    def test_scene_add_duplicate_node_fails(self):
        """Adding duplicate node fails."""
        from narrative import Scene, DialogNode

        scene = Scene("intro", "Intro", "n1")
        node1 = DialogNode("n1", "Text1")
        node2 = DialogNode("n1", "Text2")
        scene.add_node(node1)
        with pytest.raises(ValueError):
            scene.add_node(node2)

    def test_scene_get_node(self):
        """Nodes can be retrieved by ID."""
        from narrative import Scene, DialogNode

        scene = Scene("intro", "Intro", "n1")
        node = DialogNode("n1", "Text")
        scene.add_node(node)
        retrieved = scene.get_node("n1")
        assert retrieved is not None
        assert retrieved.text == "Text"

    def test_scene_repr(self):
        """Scene repr shows ID, name, node count."""
        from narrative import Scene, DialogNode

        scene = Scene("intro", "Intro Scene", "start")
        scene.add_node(DialogNode("start", "Begin"))
        scene.add_node(DialogNode("n2", "Continue"))
        repr_str = repr(scene)
        assert "intro" in repr_str
        assert "2 nodes" in repr_str


class TestDialogTree:
    """Tests for DialogTree class."""

    def test_dialog_tree_creation(self):
        """DialogTree can be created with name."""
        from narrative import DialogTree

        tree = DialogTree("Main Quest", version="1.0")
        assert tree.name == "Main Quest"
        assert tree.version == "1.0"
        assert len(tree.scenes) == 0

    def test_add_scene(self):
        """Scenes can be added to tree."""
        from narrative import DialogTree, Scene

        tree = DialogTree("Quest")
        scene = Scene("s1", "First Scene", "start")
        tree.add_scene(scene)
        assert "s1" in tree.scenes

    def test_add_duplicate_scene_fails(self):
        """Adding duplicate scene fails."""
        from narrative import DialogTree, Scene

        tree = DialogTree("Quest")
        scene1 = Scene("s1", "Scene1", "start")
        scene2 = Scene("s1", "Scene2", "start")
        tree.add_scene(scene1)
        with pytest.raises(ValueError):
            tree.add_scene(scene2)

    def test_start_scene(self):
        """Scene can be started from tree."""
        from narrative import DialogTree, Scene, DialogNode

        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "start")
        node = DialogNode("start", "Hello!")
        scene.add_node(node)
        tree.add_scene(scene)

        current = tree.start_scene("intro")
        assert current is not None
        assert current.node_id == "start"

    def test_start_nonexistent_scene_fails(self):
        """Starting nonexistent scene fails."""
        from narrative import DialogTree

        tree = DialogTree("Quest")
        with pytest.raises(ValueError):
            tree.start_scene("nonexistent")

    def test_start_scene_invalid_start_node(self):
        """Starting scene with invalid start node fails."""
        from narrative import DialogTree, Scene

        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "nonexistent_start")
        tree.add_scene(scene)
        with pytest.raises(ValueError):
            tree.start_scene("intro")

    def test_get_current_node(self):
        """Current dialog node can be retrieved."""
        from narrative import DialogTree, Scene, DialogNode

        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "start")
        node = DialogNode("start", "Text")
        scene.add_node(node)
        tree.add_scene(scene)
        tree.start_scene("intro")

        current = tree.get_current_node()
        assert current is not None
        assert current.node_id == "start"

    def test_advance_with_choices(self):
        """Can advance to choice-based branches."""
        from narrative import DialogTree, Scene, DialogNode

        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "choice")
        choice_node = DialogNode("choice", "Pick one")
        choice_node.add_choice("Option A", "path_a")
        choice_node.add_choice("Option B", "path_b")
        path_a = DialogNode("path_a", "You chose A")
        scene.add_node(choice_node)
        scene.add_node(path_a)
        tree.add_scene(scene)

        tree.start_scene("intro")
        # Advance by index (1-based)
        next_node = tree.advance_node(1)
        assert next_node is not None
        assert next_node.node_id == "path_a"

    def test_advance_by_label(self):
        """Can advance by choice label."""
        from narrative import DialogTree, Scene, DialogNode

        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "choice")
        choice_node = DialogNode("choice", "Pick one")
        choice_node.add_choice("Flee", "run")
        path_run = DialogNode("run", "You ran away")
        scene.add_node(choice_node)
        scene.add_node(path_run)
        tree.add_scene(scene)

        tree.start_scene("intro")
        next_node = tree.advance_node("Flee")
        assert next_node is not None
        assert next_node.node_id == "run"

    def test_encode(self):
        """DialogTree can be encoded to bytes."""
        from narrative import DialogTree, Scene, DialogNode

        tree = DialogTree("Quest", version="1.0")
        scene = Scene("intro", "Intro", "start")
        node = DialogNode("start", "Text")
        scene.add_node(node)
        tree.add_scene(scene)

        data = tree.encode()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_repr(self):
        """DialogTree repr shows name, version, scene count."""
        from narrative import DialogTree, Scene

        tree = DialogTree("Main Quest", version="1.5")
        tree.add_scene(Scene("s1", "Scene1", "start"))
        repr_str = repr(tree)
        assert "Main Quest" in repr_str
        assert "v1.5" in repr_str
        assert "1 scenes" in repr_str


class TestStoryManager:
    """Tests for StoryManager class."""

    def test_manager_creation(self):
        """StoryManager initializes empty."""
        from narrative import StoryManager

        mgr = StoryManager()
        assert len(mgr.trees) == 0
        assert mgr.active_tree is None

    def test_register_tree(self):
        """Narrative trees can be registered."""
        from narrative import StoryManager, DialogTree

        mgr = StoryManager()
        tree = DialogTree("Main Quest")
        mgr.register_tree(tree)
        assert "Main Quest" in mgr.trees

    def test_register_duplicate_tree_fails(self):
        """Registering duplicate tree fails."""
        from narrative import StoryManager, DialogTree

        mgr = StoryManager()
        tree1 = DialogTree("Quest")
        tree2 = DialogTree("Quest")
        mgr.register_tree(tree1)
        with pytest.raises(ValueError):
            mgr.register_tree(tree2)

    def test_get_tree(self):
        """Trees can be retrieved."""
        from narrative import StoryManager, DialogTree

        mgr = StoryManager()
        tree = DialogTree("Campaign")
        mgr.register_tree(tree)
        retrieved = mgr.get_tree("Campaign")
        assert retrieved is not None
        assert retrieved.name == "Campaign"

    def test_start_tree(self):
        """Can start playing a tree."""
        from narrative import StoryManager, DialogTree, Scene, DialogNode

        mgr = StoryManager()
        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "start")
        node = DialogNode("start", "Text")
        scene.add_node(node)
        tree.add_scene(scene)
        mgr.register_tree(tree)

        current = mgr.start_tree("Quest", "intro")
        assert current is not None
        assert mgr.active_tree is tree

    def test_advance(self):
        """Can advance dialog through manager."""
        from narrative import StoryManager, DialogTree, Scene, DialogNode

        mgr = StoryManager()
        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "choice")
        choice = DialogNode("choice", "Pick")
        choice.add_choice("Yes", "next")
        next_node = DialogNode("next", "Good!")
        scene.add_node(choice)
        scene.add_node(next_node)
        tree.add_scene(scene)
        mgr.register_tree(tree)

        mgr.start_tree("Quest", "intro")
        result = mgr.advance(1)
        assert result is not None
        assert result.node_id == "next"

    def test_get_current_node_via_manager(self):
        """Can get current node through manager."""
        from narrative import StoryManager, DialogTree, Scene, DialogNode

        mgr = StoryManager()
        tree = DialogTree("Quest")
        scene = Scene("intro", "Intro", "start")
        node = DialogNode("start", "Text")
        scene.add_node(node)
        tree.add_scene(scene)
        mgr.register_tree(tree)

        mgr.start_tree("Quest", "intro")
        current = mgr.get_current_node()
        assert current is not None
        assert current.text == "Text"

    def test_list_trees(self):
        """All trees can be listed."""
        from narrative import StoryManager, DialogTree

        mgr = StoryManager()
        mgr.register_tree(DialogTree("Quest1"))
        mgr.register_tree(DialogTree("Quest2"))
        trees = mgr.list_trees()
        assert len(trees) == 2

    def test_repr(self):
        """StoryManager repr shows tree count."""
        from narrative import StoryManager, DialogTree

        mgr = StoryManager()
        mgr.register_tree(DialogTree("Quest"))
        repr_str = repr(mgr)
        assert "1 trees" in repr_str


class TestGlobalManager:
    """Tests for global story manager."""

    def test_global_manager_exists(self):
        """Global manager instance exists."""
        from narrative import manager

        assert manager is not None


class TestLoadNarrativeFromJSON:
    """Tests for JSON narrative loading."""

    def test_load_narrative_from_json(self):
        """Narratives can be loaded from JSON."""
        from narrative import load_narrative_from_json

        assets = {
            "narratives": {
                "Main Quest": {
                    "version": "1.0",
                    "scenes": {
                        "intro": {
                            "name": "Introduction",
                            "start": "node1",
                            "nodes": {
                                "node1": {
                                    "text": "Welcome!",
                                    "speaker": "Sage",
                                    "choices": [
                                        {"label": "Listen", "next": "node2"}
                                    ],
                                }
                            },
                        }
                    },
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "story.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            mgr = load_narrative_from_json(str(json_path))
            tree = mgr.get_tree("Main Quest")
            assert tree is not None
            assert tree.name == "Main Quest"

    def test_load_multiple_scenes(self):
        """Multiple scenes can be loaded."""
        from narrative import load_narrative_from_json

        assets = {
            "narratives": {
                "Quest": {
                    "version": "1.0",
                    "scenes": {
                        "intro": {
                            "name": "Intro",
                            "start": "start",
                            "nodes": {"start": {"text": "Begin"}},
                        },
                        "climax": {
                            "name": "Climax",
                            "start": "peak",
                            "nodes": {"peak": {"text": "Final battle"}},
                        },
                    },
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "story.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            mgr = load_narrative_from_json(str(json_path))
            tree = mgr.get_tree("Quest")
            assert len(tree.scenes) == 2

    def test_load_missing_file_fails(self):
        """Loading missing file raises FileNotFoundError."""
        from narrative import load_narrative_from_json

        with pytest.raises(FileNotFoundError):
            load_narrative_from_json("/nonexistent/story.json")
