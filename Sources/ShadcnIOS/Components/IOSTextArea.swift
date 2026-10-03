import SwiftUI

public struct IOSTextArea: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    @Environment(\.isEnabled) private var isEnabled
    @ScaledMetric(relativeTo: .body) private var editorHeight: CGFloat = 110
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

    public var body: some View {
        let colors = theme.palette(for: scheme)
        let outline = error == nil ? (focused ? colors.primary : colors.input) : colors.destructiveText
        VStack(alignment: .leading, spacing: theme.spacing.xs) {
            Text(label).font(.subheadline.weight(.medium))
            TextEditor(text: $text)
                .focused($focused)
                .foregroundStyle(isEnabled ? colors.foreground : colors.mutedForeground)
                .frame(height: editorHeight)
                .padding(theme.spacing.xxs)
                .scrollContentBackground(.hidden)
                .background(isEnabled ? colors.background : colors.muted, in: RoundedRectangle(cornerRadius: theme.radii.control))
                .overlay {
                    RoundedRectangle(cornerRadius: theme.radii.control)
                        .strokeBorder(outline, lineWidth: focused || error != nil ? 2 : 1)
                }
                .accessibilityLabel(label)
                .accessibilityHint(error ?? hint ?? "")
            if let error {
                Label(error, systemImage: "exclamationmark.circle")
                    .font(.footnote).foregroundStyle(colors.destructiveText)
            } else if let hint {
                Text(hint).font(.footnote).foregroundStyle(colors.mutedForeground)
            }
        }
    }
}
