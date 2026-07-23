package com.metagame

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class TicTacToeGame : MiniGame {
    override val id: String = "tic_tac_toe"
    override val title: String = "Tic-Tac-Toe"
    override val description: String = "Classic 3x3 turn-based grid game. Align 3 marks to win!"
    override val iconName: String = "tic_tac_toe_icon"

    enum class Cell { EMPTY, X, O }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    override fun Content(onExit: () -> Unit) {
        var board by remember { mutableStateOf(List(9) { Cell.EMPTY }) }
        var isXTurn by remember { mutableStateOf(true) }

        val winner = checkWinner(board)
        val isDraw = !board.contains(Cell.EMPTY) && winner == null

        fun makeMove(index: Int) {
            if (board[index] == Cell.EMPTY && winner == null) {
                board = board.toMutableList().apply {
                    this[index] = if (isXTurn) Cell.X else Cell.O
                }
                isXTurn = !isXTurn
            }
        }

        fun resetGame() {
            board = List(9) { Cell.EMPTY }
            isXTurn = true
        }

        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text(text = "Tic-Tac-Toe", fontWeight = FontWeight.Bold) },
                    navigationIcon = {
                        IconButton(onClick = onExit) {
                            Icon(imageVector = Icons.Default.ArrowBack, contentDescription = "Back to Dashboard")
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surfaceColorAtElevation(3.dp)
                    )
                )
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                // Game Status Header
                val statusText = when {
                    winner != null -> "Winner: $winner"
                    isDraw -> "It's a Draw!"
                    else -> "Player: ${if (isXTurn) "X" else "O"}'s Turn"
                }

                Text(
                    text = statusText,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.Bold,
                    color = when {
                        winner != null -> MaterialTheme.colorScheme.primary
                        isDraw -> MaterialTheme.colorScheme.secondary
                        else -> MaterialTheme.colorScheme.onBackground
                    },
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                // 3x3 Grid
                Column(
                    modifier = Modifier
                        .wrapContentSize()
                        .clip(RoundedCornerShape(12.dp))
                        .background(MaterialTheme.colorScheme.surfaceVariant)
                        .padding(8.dp)
                ) {
                    for (row in 0 until 3) {
                        Row {
                            for (col in 0 until 3) {
                                val index = row * 3 + col
                                GridCell(
                                    cellValue = board[index],
                                    onClick = { makeMove(index) }
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                // Restart & Controls
                Button(
                    onClick = { resetGame() },
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = PaddingValues(horizontal = 24.dp, vertical = 12.dp)
                ) {
                    Icon(imageVector = Icons.Default.Refresh, contentDescription = "Restart")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = "Restart Game", fontSize = 16.sp)
                }
            }
        }
    }

    @Composable
    private fun GridCell(cellValue: Cell, onClick: () -> Unit) {
        val displayChar = when (cellValue) {
            Cell.EMPTY -> ""
            Cell.X -> "X"
            Cell.O -> "O"
        }

        val cellColor = when (cellValue) {
            Cell.X -> MaterialTheme.colorScheme.primary
            Cell.O -> MaterialTheme.colorScheme.secondary
            else -> Color.Unspecified
        }

        Box(
            modifier = Modifier
                .size(90.dp)
                .padding(4.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(MaterialTheme.colorScheme.surface)
                .border(2.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.5f), RoundedCornerShape(8.dp))
                .clickable(enabled = cellValue == Cell.EMPTY) { onClick() },
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = displayChar,
                fontSize = 40.sp,
                fontWeight = FontWeight.Bold,
                color = cellColor
            )
        }
    }

    /**
     * Determines the winner from the current board configurations.
     */
    fun checkWinner(board: List<Cell>): Cell? {
        val winPositions = listOf(
            listOf(0, 1, 2), listOf(3, 4, 5), listOf(6, 7, 8), // Rows
            listOf(0, 3, 6), listOf(1, 4, 7), listOf(2, 5, 8), // Columns
            listOf(0, 4, 8), listOf(2, 4, 6)                  // Diagonals
        )

        for (pos in winPositions) {
            if (board[pos[0]] != Cell.EMPTY &&
                board[pos[0]] == board[pos[1]] &&
                board[pos[1]] == board[pos[2]]
            ) {
                return board[pos[0]]
            }
        }
        return null
    }
}
