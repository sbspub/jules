package com.metagame

import androidx.compose.runtime.Composable
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class GameRegistryTest {

    @Before
    fun setUp() {
        GameRegistry.clearRegistry()
    }

    @Test
    fun testRegisterAndRetrieveGame() {
        val dummyGame = object : MiniGame {
            override val id: String = "dummy"
            override val title: String = "Dummy Game"
            override val description: String = "Test Game"
            override val iconName: String = "dummy_icon"

            @Composable
            override fun Content(onExit: () -> Unit) {}
        }

        GameRegistry.registerGame(dummyGame)

        val retrieved = GameRegistry.getGameById("dummy")
        assertNotNull(retrieved)
        assertEquals("Dummy Game", retrieved?.title)
        assertEquals(1, GameRegistry.getGames().size)
    }

    @Test
    fun testGetNonExistentGame() {
        assertNull(GameRegistry.getGameById("non_existent"))
    }
}
