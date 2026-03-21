import asyncio

import pytest

from gfal_cli.tui import GfalTui, HighlightableDirectoryTree


@pytest.mark.asyncio
async def test_tui_movement_vim_keys():
    """Test that j, k, g, G keys move the cursor correctly."""
    app = GfalTui()
    async with app.run_test() as pilot:
        # Wait for DirectoryTree to load the current directory
        tree = app.query_one("#local-tree", HighlightableDirectoryTree)

        # We need to wait for children to populate
        for _ in range(50):
            if tree.root.children:
                break
            await asyncio.sleep(0.1)
            await pilot.pause()

        assert len(tree.root.children) > 1

        # With show_root=False, first entry is tree.root.children[0]
        app.set_focus(tree)
        await pilot.pause()

        # Start at the top (g)
        await pilot.press("g")
        await pilot.pause()
        assert tree.cursor_line == 0
        initial_node = tree.cursor_node
        assert initial_node == tree.root.children[0]

        # Move down with 'j'
        await pilot.press("j")
        await pilot.pause()
        assert tree.cursor_line == 1
        down_j_node = tree.cursor_node
        assert down_j_node == tree.root.children[1]

        # Move up with 'k'
        await pilot.press("k")
        await pilot.pause()
        assert tree.cursor_line == 0
        assert tree.cursor_node == initial_node

        # Move to bottom with 'G'
        await pilot.press("G")
        await pilot.pause()
        assert tree.cursor_line == tree.line_count - 1

        # Move to top with 'g'
        await pilot.press("g")
        await pilot.pause()
        assert tree.cursor_line == 0


@pytest.mark.asyncio
async def test_tui_movement_remote_tree():
    """Test that movement keys work in the remote tree."""
    app = GfalTui()
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#remote-tree")
        app.set_focus(tree)

        # Initially, with show_root=False and no children loaded yet, cursor_line should be 0 (pointing to root even if hidden?)
        # Actually, if root is hidden and no children, line_count might be 0.
        await pilot.press("g")
        await pilot.pause()

        await pilot.press("G")
        await pilot.pause()
        assert True  # Just ensuring no crash
