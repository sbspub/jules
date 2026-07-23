package com.metagame

import androidx.compose.runtime.Composable

/**
 * Interface that all modular mini-games must implement to be added to the Meta Game app.
 */
interface MiniGame {
    /**
     * Unique identifier for the mini-game.
     */
    val id: String

    /**
     * Display name of the mini-game.
     */
    val title: String

    /**
     * Brief description of the mini-game's rules or objective.
     */
    val description: String

    /**
     * Material icon name or category (optional, for decorative purposes).
     */
    val iconName: String

    /**
     * The main composable screen for the game.
     * @param onExit callback to trigger when the user exits the mini-game.
     */
    @Composable
    fun Content(onExit: () -> Unit)
}
