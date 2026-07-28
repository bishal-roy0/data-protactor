package com.karna.companion.config

import android.content.Context
import com.karna.companion.BuildConfig

class SettingsStore(context: Context) {
    private val preferences = context.getSharedPreferences("karna_settings", Context.MODE_PRIVATE)

    fun apiBaseUrl(): String = preferences.getString("api_base_url", BuildConfig.DEFAULT_API_BASE_URL)
        ?: BuildConfig.DEFAULT_API_BASE_URL

    fun saveApiBaseUrl(value: String) {
        preferences.edit().putString("api_base_url", value.trim()).apply()
    }

    fun hasAcceptedPrivacyNotice(): Boolean = preferences.getBoolean("privacy_notice_accepted", false)

    fun acceptPrivacyNotice() {
        preferences.edit().putBoolean("privacy_notice_accepted", true).apply()
    }
}
