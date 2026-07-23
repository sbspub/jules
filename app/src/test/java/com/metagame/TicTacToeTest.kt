package com.metagame

import org.junit.Assert.*
import org.junit.Test

class TicTacToeTest {

    private val ticTacToe = TicTacToeGame()

    @Test
    fun testInitialBoardHasNoWinner() {
        val board = List(9) { TicTacToeGame.Cell.EMPTY }
        assertNull(ticTacToe.checkWinner(board))
    }

    @Test
    fun testRowWinX() {
        val board = listOf(
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.X, TicTacToeGame.Cell.X,
            TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.O, TicTacToeGame.Cell.O,
            TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.EMPTY
        )
        assertEquals(TicTacToeGame.Cell.X, ticTacToe.checkWinner(board))
    }

    @Test
    fun testColumnWinO() {
        val board = listOf(
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.O, TicTacToeGame.Cell.EMPTY,
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.O, TicTacToeGame.Cell.EMPTY,
            TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.O, TicTacToeGame.Cell.X
        )
        assertEquals(TicTacToeGame.Cell.O, ticTacToe.checkWinner(board))
    }

    @Test
    fun testDiagonalWinX() {
        val board = listOf(
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.O,
            TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.X, TicTacToeGame.Cell.EMPTY,
            TicTacToeGame.Cell.O, TicTacToeGame.Cell.EMPTY, TicTacToeGame.Cell.X
        )
        assertEquals(TicTacToeGame.Cell.X, ticTacToe.checkWinner(board))
    }

    @Test
    fun testDrawConfiguration() {
        val board = listOf(
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.O, TicTacToeGame.Cell.X,
            TicTacToeGame.Cell.X, TicTacToeGame.Cell.O, TicTacToeGame.Cell.O,
            TicTacToeGame.Cell.O, TicTacToeGame.Cell.X, TicTacToeGame.Cell.X
        )
        assertNull(ticTacToe.checkWinner(board))
    }
}
