//
//  SkinFitApp.swift
//  SkinFit
//
//  Created by Katelyn Fritz
//

import SwiftUI

@main
struct SkinFitApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView(classifier: ImageClassifier())
        }
    }
}
