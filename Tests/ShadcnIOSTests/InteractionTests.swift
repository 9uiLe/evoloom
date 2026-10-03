@testable import ShadcnIOS
import SwiftUI
import XCTest

@MainActor
final class InteractionTests: XCTestCase {
    func testDisplayOnlyComponentsCompareParentInputs() {
        XCTAssertEqual(IOSBadge("Ready", variant: .success), IOSBadge("Ready", variant: .success))
        XCTAssertNotEqual(IOSBadge("Ready", variant: .success), IOSBadge("Failed", variant: .destructive))
        XCTAssertEqual(IOSCardHeader("Account", detail: "Active"), IOSCardHeader("Account", detail: "Active"))
        XCTAssertNotEqual(IOSSkeleton(height: 20), IOSSkeleton(height: 24))
        XCTAssertEqual(IOSSeparator(), IOSSeparator())
    }

    func testButtonActionGate() {
        var calls = 0
        let ready = IOSButton("Send") { calls += 1 }
        let loading = IOSButton("Send", isLoading: true) { calls += 1 }
        ready.trigger(isEnabled: false)
        loading.trigger(isEnabled: true)
        XCTAssertEqual(calls, 0)
        ready.trigger(isEnabled: true)
        XCTAssertEqual(calls, 1)
    }

    func testInputBinding() {
        let state = TextState()
        let binding = Binding<String>(get: { state.text }, set: { state.text = $0 })
        let input = IOSInput("Name", text: binding)
        XCTAssertEqual(input.text, "")
        input.text = "Alex"
        XCTAssertEqual(state.text, "Alex")

        let area = IOSTextArea("Notes", text: binding)
        area.text = "A note"
        XCTAssertEqual(state.text, "A note")
    }

    func testSwitchBinding() {
        let state = ToggleState()
        let binding = Binding<Bool>(get: { state.isOn }, set: { state.isOn = $0 })
        let control = IOSSwitch("Updates", isOn: binding)
        XCTAssertFalse(control.isOn)
        control.isOn = true
        XCTAssertTrue(state.isOn)
    }
}

private final class TextState {
    var text = ""
}

private final class ToggleState {
    var isOn = false
}
