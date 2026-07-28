package com.karna.companion

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import com.karna.companion.ui.KarnaApp
import com.karna.companion.ui.KarnaViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: KarnaViewModel by viewModels { KarnaViewModel.factory(application) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.loadSharedIntent(intent)
        setContent { KarnaApp(viewModel) }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        viewModel.loadSharedIntent(intent)
    }
}
