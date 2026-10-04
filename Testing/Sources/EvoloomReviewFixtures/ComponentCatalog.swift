import Evoloom
import SwiftUI

/// Development-only Preview fixture; the Evoloom library product does not include it.
struct ComponentCatalog: View {
    @Environment(\.iosDesignTokens) private var tokens
    @State private var name = ""
    @State private var note = ""
    @State private var enabled = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: tokens.spacing.lg) {
                Text("Components").font(.largeTitle.bold())
                ForEach(IOSButtonVariant.allCases, id: \.self) { variant in
                    IOSButton("Continue", variant: variant) {}
                }
                IOSButton("Saving", isLoading: true) {}
                IOSButton("Unavailable") {}.disabled(true)
                IOSCard {
                    VStack(alignment: .leading, spacing: tokens.spacing.md) {
                        IOSCardHeader("Project", detail: "A reusable content container")
                        IOSSeparator()
                        IOSBadge("Ready", symbol: "checkmark", variant: .success)
                    }
                }
                IOSInput("Name", text: $name, placeholder: "Your name", error: "Enter at least two characters.")
                IOSTextArea("Notes", text: $note, hint: "Add useful context.")
                IOSSwitch("Notifications", isOn: $enabled, detail: "Receive updates on this device.")
                IOSInlineAlert("Connection unavailable", message: "Try again when you are online.", variant: .error)
                IOSEmptyState("Nothing here yet", message: "Create an item to get started.") {
                    IOSButton("Create item") {}
                }
                IOSSkeleton()
            }
            .padding(tokens.spacing.md)
        }
    }
}

enum CollectionState: String, CaseIterable, Identifiable {
    case normal, empty, loading, error
    var id: String {
        rawValue
    }
}

struct ExampleCollectionView: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @State private var search = ""
    @State private var state: CollectionState = .normal
    @State private var showingNew = false

    init(initialState: CollectionState = .normal) {
        _state = State(initialValue: initialState)
    }

    var body: some View {
        NavigationStack {
            CollectionContent(state: $state, search: search)
                .navigationTitle("Collection")
                .searchable(text: $search)
                .navigationDestination(for: String.self) { item in
                    Text(item).navigationTitle(item)
                }
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("New", systemImage: "plus") { showingNew = true }
                    }
                }
                .sheet(isPresented: $showingNew) {
                    NavigationStack {
                        Text("Create item").navigationTitle("New item")
                            .toolbar {
                                ToolbarItem(placement: .confirmationAction) {
                                    Button("Done") { showingNew = false }
                                }
                            }
                    }
                }
        }
        .tint(scheme == .dark ? tokens.dark.foreground : tokens.light.foreground)
    }
}

struct CollectionContent: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Binding var state: CollectionState
    let search: String

    private let items = [
        (title: "Design notes", detail: "Research decisions and open questions", status: "Ready"),
        (title: "Release checklist", detail: "Three tasks need review", status: "Review"),
        (title: "Research summary", detail: "Findings from the last interview", status: "Draft"),
    ]

    init(state: Binding<CollectionState>, search: String = "") {
        _state = state
        self.search = search
    }

    var body: some View {
        List {
            Section {
                Text("Keep project decisions and next steps together.")
            } header: {
                Text("Overview")
            }
            Section("Preview state") {
                Picker("State", selection: $state) {
                    ForEach(CollectionState.allCases) { item in
                        Text(item.rawValue.capitalized).tag(item)
                    }
                }
            }
            Section("Items") {
                switch state {
                case .normal:
                    ForEach(items.filter { search.isEmpty || $0.title.localizedCaseInsensitiveContains(search) }, id: \.title) { item in
                        NavigationLink(value: item.title) {
                            VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
                                Text(item.title).font(.headline)
                                Text(item.detail).font(.subheadline).foregroundStyle(.secondary)
                                IOSBadge(item.status, variant: item.status == "Ready" ? .success : .secondary)
                            }
                        }
                    }
                case .empty:
                    IOSEmptyState("No items", message: "Add your first item.")
                case .loading:
                    VStack(alignment: .leading) {
                        Text("Loading items")
                        IOSSkeleton()
                    }
                case .error:
                    IOSInlineAlert("Items unavailable", message: "Check your connection and retry.", variant: .error)
                }
            }
        }
    }
}

private struct SwitchStatesPreview: View {
    @State private var notifications = true
    @State private var updates = false

    var body: some View {
        VStack(spacing: 24) {
            IOSSwitch("Notifications", isOn: $notifications, detail: "Receive updates on this device.")
            IOSSwitch("Updates", isOn: $updates, detail: "Receive updates on this device.")
        }
        .padding()
    }
}

#Preview("Catalog - light") {
    ComponentCatalog().preferredColorScheme(.light)
}

#Preview("Catalog - dark") {
    ComponentCatalog().preferredColorScheme(.dark)
}

#Preview("Switch states - dark") {
    SwitchStatesPreview().preferredColorScheme(.dark)
}

#Preview("Collection - light") {
    ExampleCollectionView().preferredColorScheme(.light)
}

#Preview("Collection - dark") {
    ExampleCollectionView().preferredColorScheme(.dark)
}

#Preview("Collection - empty") {
    ExampleCollectionView(initialState: .empty)
}

#Preview("Collection - loading") {
    ExampleCollectionView(initialState: .loading)
}

#Preview("Collection - error") {
    ExampleCollectionView(initialState: .error)
}

#Preview("Adjusted design tokens") {
    var tokens = IOSDesignTokens.neutral
    tokens.light.primary = .indigo
    tokens.light.primaryForeground = .white
    tokens.radii.control = 16
    tokens.spacing.lg = 28
    return ComponentCatalog().iosDesignTokens(tokens)
}
