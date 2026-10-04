import SwiftUI

/// Internal preview fixtures compile with the library and are not public API.
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

struct ExampleCollectionView: View {
    enum FixtureState: String, CaseIterable, Identifiable {
        case normal, empty, loading, error
        var id: String {
            rawValue
        }
    }

    @State private var search = ""
    @State private var state: FixtureState = .normal
    @State private var showingNew = false

    private let items = ["Design notes", "Release checklist", "Research summary"]

    var body: some View {
        NavigationStack {
            List {
                Section("Preview state") {
                    Picker("State", selection: $state) {
                        ForEach(FixtureState.allCases) { item in
                            Text(item.rawValue.capitalized).tag(item)
                        }
                    }
                }
                Section("Items") {
                    switch state {
                    case .normal:
                        ForEach(items.filter { search.isEmpty || $0.localizedCaseInsensitiveContains(search) }, id: \.self) { item in
                            NavigationLink(item, value: item)
                        }
                    case .empty:
                        IOSEmptyState("No items", message: "Add your first item.")
                    case .loading:
                        IOSSkeleton().accessibilityLabel("Loading items")
                    case .error:
                        IOSInlineAlert("Items unavailable", message: "Check your connection and retry.", variant: .error)
                    }
                }
            }
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

#Preview("Collection") {
    ExampleCollectionView()
}

#Preview("Adjusted design tokens") {
    var tokens = IOSDesignTokens.neutral
    tokens.light.primary = .indigo
    tokens.light.primaryForeground = .white
    tokens.radii.control = 16
    tokens.spacing.lg = 28
    return ComponentCatalog().iosDesignTokens(tokens)
}
