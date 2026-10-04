import SwiftUI

public struct IOSInput: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @Environment(\.isEnabled) private var isEnabled
    @FocusState private var focused: Bool
    @Binding var text: String
    public let label: String
    public let placeholder: String
    public var hint: String?
    public var error: String?
    public var secure: Bool
    public var keyboardType: UIKeyboardType
    public var contentType: UITextContentType?

    public init(
        _ label: String, text: Binding<String>, placeholder: String = "",
        hint: String? = nil, error: String? = nil, secure: Bool = false,
        keyboardType: UIKeyboardType = .default, contentType: UITextContentType? = nil
    ) {
        self.label = label
        _text = text
        self.placeholder = placeholder
        self.hint = hint
        self.error = error
        self.secure = secure
        self.keyboardType = keyboardType
        self.contentType = contentType
    }

    public var body: some View {
        let colors = tokens.palette(for: scheme)
        VStack(alignment: .leading, spacing: tokens.spacing.xs) {
            Text(label).font(tokens.typography.fieldLabel)
            Group {
                if secure {
                    SecureField(placeholder, text: $text)
                } else {
                    TextField(placeholder, text: $text)
                }
            }
            .keyboardType(keyboardType)
            .textContentType(contentType)
            .focused($focused)
            .foregroundStyle(isEnabled ? colors.foreground : colors.mutedForeground)
            .padding(tokens.spacing.sm)
            .frame(minHeight: tokens.controls.minimumHeight)
            .background(isEnabled ? colors.background : colors.muted, in: RoundedRectangle(cornerRadius: tokens.radii.control))
            .overlay {
                RoundedRectangle(cornerRadius: tokens.radii.control)
                    .strokeBorder(
                        error == nil ? (focused ? colors.primary : colors.input) : colors.destructiveText,
                        lineWidth: focused || error != nil ? tokens.controls.emphasizedBorderWidth : tokens.controls.borderWidth
                    )
            }
            .accessibilityLabel(label)
            .accessibilityHint(error ?? hint ?? "")
            if let error {
                Label(error, systemImage: "exclamationmark.circle")
                    .font(tokens.typography.supporting)
                    .foregroundStyle(colors.destructiveText)
            } else if let hint {
                Text(hint).font(tokens.typography.supporting).foregroundStyle(colors.mutedForeground)
            }
        }
    }
}
