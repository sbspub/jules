package com.metagame

/**
 * Registry to manage and retrieve available modular mini-games in the Meta Game app.
 */
object GameRegistry {
    private val registeredGames = mutableMapOf<String, MiniGame>()

    /**
     * Registers a mini-game to make it available in the dashboard.
     */
    fun registerGame(game: MiniGame) {
        registeredGames[game.id] = game
    }

    /**
     * Retrieves all currently registered mini-games.
     */
    fun getGames(): List<MiniGame> {
        return registeredGames.values.toList()
    }

    /**
     * Retrieves a mini-game by its unique ID.
     */
    fun getGameById(id: String): MiniGame? {
        return registeredGames[id]
    }

    /**
     * Clears all registered mini-games (useful for testing or resetting).
     */
    fun clearRegistry() {
        registeredGames.clear()
    }
}
