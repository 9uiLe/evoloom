import SwiftUI

public struct IOSInput: View {
    @Environment(\.iosTheme) private var theme
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
        let colors = theme.palette(for: scheme)
        VStack(alignment: .leading, spacing: theme.spacing.xs) {
            Text(label).font(.subheadline.weight(.medium))
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
            .padding(theme.spacing.sm)
            .frame(minHeight: 44)
            .background(isEnabled ? colors.background : colors.muted, in: RoundedRectangle(cornerRadius: theme.radii.control))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radii.control)
                    .strokeBorder(error == nil ? (focused ? colors.primary : colors.input) : colors.destructiveText, lineWidth: focused || error != nil ? 2 : 1)
            }
            .accessibilityLabel(label)
            .accessibilityHint(error ?? hint ?? "")
            if let error {
                Label(error, systemImage: "exclamationmark.circle")
                    .font(.footnote)
                    .foregroundStyle(colors.destructiveText)
            } else if let hint {
                Text(hint).font(.footnote).foregroundStyle(colors.mutedForeground)
            }
        }
    }
}
