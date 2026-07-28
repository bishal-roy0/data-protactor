package com.karna.companion.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.karna.companion.model.AnalysisResponse
import com.karna.companion.share.SharedContent

private val KarnaBlue = Color(0xFF35A8FF)
private val KarnaPink = Color(0xFFFF4FA3)
private val KarnaRed = Color(0xFFFF4D5C)
private val KarnaBlack = Color(0xFF07111F)

@Composable
fun KarnaApp(viewModel: KarnaViewModel) {
    val state by viewModel.state.collectAsState()
    MaterialTheme(colorScheme = MaterialTheme.colorScheme.copy(primary = KarnaBlue, secondary = KarnaPink)) {
        Scaffold(
            topBar = { KarnaTopBar(onSettings = viewModel::openSettings) },
            containerColor = KarnaBlack,
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text("Personal safety companion", color = KarnaBlue, fontWeight = FontWeight.Bold)
                Text(
                    "Scan only content you choose to share. Karna is advisory; you decide what to do next.",
                    color = Color.White,
                    style = MaterialTheme.typography.bodyLarge,
                )
                SharedReview(state.sharedContent)
                Button(
                    onClick = viewModel::requestScan,
                    enabled = !state.isScanning,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(if (state.isScanning) "Scanning…" else "Scan with Karna")
                }
                state.error?.let { Text(it, color = KarnaRed) }
                state.result?.let { ResultCard(it) }
                Text(
                    "Karna does not read private messages, scan your device, block downloads, or remove malware.",
                    color = Color.LightGray,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
    if (state.showSettings) SettingsDialog(state.apiBaseUrl, viewModel::updateApiBaseUrl, viewModel::saveSettings, viewModel::closeSettings)
    if (state.showPrivacyNotice) PrivacyDialog(viewModel::acceptPrivacyAndScan, viewModel::dismissPrivacyNotice)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun KarnaTopBar(onSettings: () -> Unit) {
    TopAppBar(
        title = { Text("Karna", color = Color.White, fontWeight = FontWeight.Bold) },
        actions = { IconButton(onClick = onSettings) { Icon(Icons.Default.Settings, "Settings", tint = KarnaBlue) } },
    )
}

@Composable
private fun SharedReview(content: SharedContent) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Shared content review", fontWeight = FontWeight.Bold)
            when (content) {
                is SharedContent.Text -> {
                    Text("Text or link", color = KarnaBlue)
                    Text(content.value.take(700))
                }
                is SharedContent.Image -> {
                    Text("Image", color = KarnaBlue)
                    Text("A ${content.mimeType ?: "shared"} image is ready for review. It is not saved by Karna.")
                }
                SharedContent.Empty -> Text("Open a supported app, choose Share, then select Karna to review a message, link, or image.")
            }
        }
    }
}

@Composable
private fun ResultCard(result: AnalysisResponse) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Assessment", fontWeight = FontWeight.Bold)
            Row {
                Text(result.risk_level.uppercase(), color = riskColor(result.risk_level), fontWeight = FontWeight.Bold)
                Spacer(Modifier.width(16.dp))
                Text("${result.risk_score}/100")
            }
            Text("Category: ${result.threat_category.replace('_', ' ')}")
            Text("Recommended action: ${SafetyResultPresenter.actionLabel(result)}", fontWeight = FontWeight.Bold)
            Text("Confidence: ${(result.confidence * 100).toInt()}%")
            Text(result.summary)
            if (result.evidence.isNotEmpty()) {
                Text("Evidence", fontWeight = FontWeight.Bold)
                result.evidence.forEach { evidence ->
                    Text("• ${evidence.signal}: ${evidence.explanation}")
                }
            }
        }
    }
}

@Composable
private fun SettingsDialog(value: String, onValueChange: (String) -> Unit, onSave: () -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Karna API settings") },
        text = {
            Column {
                Text("Use an HTTPS API address. API keys stay on the Karna server and are never stored in this app.")
                Spacer(Modifier.height(12.dp))
                OutlinedTextField(value = value, onValueChange = onValueChange, label = { Text("API base URL") })
            }
        },
        confirmButton = { Button(onClick = onSave) { Text("Save") } },
        dismissButton = { Button(onClick = onDismiss) { Text("Cancel") } },
    )
}

@Composable
private fun PrivacyDialog(onAccept: () -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Before you scan") },
        text = { Text("Only the content you choose to share is sent to Karna for analysis. Karna does not access your private messages or scan your phone.") },
        confirmButton = { Button(onClick = onAccept) { Text("Continue") } },
        dismissButton = { Button(onClick = onDismiss) { Text("Cancel") } },
    )
}

private fun riskColor(level: String): Color = when (level) {
    "critical" -> KarnaRed
    "high" -> KarnaPink
    "safe" -> Color(0xFF4CE8C4)
    else -> KarnaBlue
}
