def main():
    """Beispiel für die Nutzung des MetaboMind-Frameworks"""
    try:
        # Initialisiere das System
        metabo = MetaboCore("config.json")
        metabo.initialize_system()
        
        # Lade vortrainierte Modelle
        metabo.gnn_manager.load_models("models/")
        
        # Starte kontinuierliche Verarbeitung
        metabo.start_continuous_processing()
        
        # Starte REST-API
        rest_api = MetaboRESTAPI(metabo.api, metabo.config, metabo.logger)
        rest_api.start_server()
        
        # Integriere etwas Wissen
        result = metabo.integrate_knowledge(
            "MetaboMind ist ein System für selbstoptimierendes Wissensmanagement, "
            "das auf dem Yin-Yang-Prinzip und Entropieminimierung basiert.")
        
        # Führe eine Abfrage durch
        query_result = metabo.process_query(
            "Wie hängt das Yin-Yang-Prinzip mit der Entropieminimierung zusammen?")
        
        # Führe einen Metabo-Zyklus aus
        cycle_result = metabo.run_metabo_cycle()
        
        # Führe eine Meta-Reflexion durch
        reflection = metabo.meta_consciousness.reflect(
            metabo.graph, metabo.regulator.yin_yang, metabo.llm)
        
        # Überwache kontinuierlich den Status
        while True:
            time.sleep(10)
            status = metabo.get_system_status()
            print(f"System Yin-Yang: {status['yin_yang']}, " 
                  f"Entropie: {status['entropy']}, " 
                  f"Knoten: {status['nodes_count']}")
    
    except KeyboardInterrupt:
        # Beenden der Verarbeitung
        metabo.stop_continuous_processing()
        rest_api.stop_server()
        metabo.save_state("checkpoints/latest/")
        print("MetaboMind-System sicher beendet.")


if __name__ == "__main__":
    main()