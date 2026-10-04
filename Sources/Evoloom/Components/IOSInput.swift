import SwiftUI

/// Use formRow only when a native Form supplies the field's surface and row boundary.
public enum IOSInputAppearance: Sendable {
    case outlined, formRow
}

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
    public var appearance: IOSInputAppearance

    public init(
        _ label: String, text: Binding<String>, placeholder: String = "",
        hint: String? = nil, error: String? = nil, secure: Bool = false,
        keyboardType: UIKeyboardType = .default, contentType: UITextContentType? = nil,
        appearance: IOSInputAppearance = .outlined
    ) {
        self.label = label
        _text = text
        self.placeholder = placeholder
        self.hint = hint
        self.error = error
        self.secure = secure
        self.keyboardType = keyboardType
        self.contentType = contentType
        self.appearance = appearance
    }

    public var body: some View {
        let colors = tokens.palette(for: scheme)
        VStack(alignment: .leading, spacing: appearance == .formRow ? tokens.spacing.xxs : tokens.spacing.xs) {
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
            .padding(appearance == .outlined ? tokens.spacing.sm : 0)
            .frame(minHeight: tokens.controls.minimumHeight)
            .background {
                if appearance == .outlined {
                    RoundedRectangle(cornerRadius: tokens.radii.control)
                        .fill(isEnabled ? colors.background : colors.muted)
                }
            }
            .overlay {
                if appearance == .outlined {
                    RoundedRectangle(cornerRadius: tokens.radii.control)
                        .strokeBorder(
                            error == nil ? (focused ? colors.primary : colors.input) : colors.destructiveText,
                            lineWidth: focused || error != nil ? tokens.controls.emphasizedBorderWidth : tokens.controls.borderWidth
                        )
                } else if focused || error != nil {
                    Rectangle()
                        .fill(error == nil ? colors.primary : colors.destructiveText)
                        .frame(height: tokens.controls.emphasizedBorderWidth)
                        .frame(maxHeight: .infinity, alignment: .bottom)
                        .allowsHitTesting(false)
                }
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
