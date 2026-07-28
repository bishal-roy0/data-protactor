package com.karna.companion.ui

import android.app.Application
import android.content.Intent
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.karna.companion.config.SettingsStore
import com.karna.companion.data.KarnaRepository
import com.karna.companion.model.AnalysisResponse
import com.karna.companion.share.SharedContent
import com.karna.companion.share.SharedContentParser
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class KarnaUiState(
    val sharedContent: SharedContent = SharedContent.Empty,
    val apiBaseUrl: String = "",
    val result: AnalysisResponse? = null,
    val error: String? = null,
    val isScanning: Boolean = false,
    val showSettings: Boolean = false,
    val showPrivacyNotice: Boolean = false,
)

class KarnaViewModel(application: Application) : AndroidViewModel(application) {
    private val settings = SettingsStore(application)
    private val repository = KarnaRepository()
    private val _state = MutableStateFlow(KarnaUiState(apiBaseUrl = settings.apiBaseUrl()))
    val state: StateFlow<KarnaUiState> = _state.asStateFlow()

    fun loadSharedIntent(intent: Intent?) {
        _state.value = _state.value.copy(
            sharedContent = SharedContentParser.fromIntent(intent),
            result = null,
            error = null,
        )
    }

    fun openSettings() { _state.value = _state.value.copy(showSettings = true) }
    fun closeSettings() { _state.value = _state.value.copy(showSettings = false) }
    fun updateApiBaseUrl(value: String) { _state.value = _state.value.copy(apiBaseUrl = value) }

    fun saveSettings() {
        settings.saveApiBaseUrl(_state.value.apiBaseUrl)
        _state.value = _state.value.copy(showSettings = false)
    }

    fun requestScan() {
        if (_state.value.sharedContent is SharedContent.Empty) {
            _state.value = _state.value.copy(error = "Share a message, link, or supported image to Karna first.")
        } else if (!settings.hasAcceptedPrivacyNotice()) {
            _state.value = _state.value.copy(showPrivacyNotice = true)
        } else {
            scan()
        }
    }

    fun acceptPrivacyAndScan() {
        settings.acceptPrivacyNotice()
        _state.value = _state.value.copy(showPrivacyNotice = false)
        scan()
    }

    fun dismissPrivacyNotice() { _state.value = _state.value.copy(showPrivacyNotice = false) }

    private fun scan() {
        val content = _state.value.sharedContent
        _state.value = _state.value.copy(isScanning = true, error = null, result = null)
        viewModelScope.launch {
            val result = when (content) {
                is SharedContent.Text -> repository.analyzeText(_state.value.apiBaseUrl, content.value)
                is SharedContent.Image -> repository.analyzeImage(
                    _state.value.apiBaseUrl,
                    getApplication<Application>().contentResolver,
                    content.uri,
                    content.mimeType,
                )
                SharedContent.Empty -> return@launch
            }
            _state.value = _state.value.copy(
                isScanning = false,
                result = result.getOrNull(),
                error = result.exceptionOrNull()?.message,
            )
        }
    }

    companion object {
        fun factory(application: Application) = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T =
                KarnaViewModel(application) as T
        }
    }
}
