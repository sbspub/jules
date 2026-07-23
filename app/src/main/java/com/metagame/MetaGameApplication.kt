package com.metagame

import android.app.Application

class MetaGameApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Register default mini-games
        GameRegistry.registerGame(TicTacToeGame())
    }
}
