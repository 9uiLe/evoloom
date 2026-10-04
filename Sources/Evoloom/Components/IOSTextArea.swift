import AppMacros
import SwiftUI

@AutoEquatableView
public struct IOSTextArea: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @Environment(\.isEnabled) private var isEnabled
    @ScaledMetric(relativeTo: .body) private var scaledReferenceHeight: CGFloat = IOSControlTokens.defaultTextAreaHeight
    @FocusState private var focused: Bool
    @Binding var text: String
    public let label: String
    public var hint: String?
    public var error: String?

    public init(_ label: String, text: Binding<String>, hint: String? = nil, error: String? = nil) {
        self.label = label
        _text = text
        self.hint = hint
        self.error = error
    }

    @ViewBuilder public var equatableBody: some View {
        let colors = tokens.palette(for: scheme)
        let outline = error == nil ? (focused ? colors.primary : colors.input) : colors.destructiveText
        VStack(alignment: .leading, spacing: tokens.spacing.xs) {
            Text(label).font(tokens.typography.fieldLabel)
            TextEditor(text: $text)
                .focused($focused)
                .foregroundStyle(isEnabled ? colors.foreground : colors.mutedForeground)
                .frame(height: scaledReferenceHeight * (tokens.controls.textAreaHeight / IOSControlTokens.defaultTextAreaHeight))
                .padding(tokens.spacing.xxs)
                .scrollContentBackground(.hidden)
                .background(isEnabled ? colors.background : colors.muted, in: RoundedRectangle(cornerRadius: tokens.radii.control))
                .overlay {
                    RoundedRectangle(cornerRadius: tokens.radii.control)
                        .strokeBorder(outline, lineWidth: focused || error != nil ? tokens.controls.emphasizedBorderWidth : tokens.controls.borderWidth)
                }
                .accessibilityLabel(label)
                .accessibilityHint(error ?? hint ?? "")
            if let error {
                Label(error, systemImage: "exclamationmark.circle")
                    .font(tokens.typography.supporting).foregroundStyle(colors.destructiveText)
            } else if let hint {
                Text(hint).font(tokens.typography.supporting).foregroundStyle(colors.mutedForeground)
            }
        }
    }
}
