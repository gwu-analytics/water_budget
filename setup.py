import methods

def setup():
    # Print header and menu options
    print('=' * 50)
    print('Master-Metered Community Violations Setup Wizard')
    print('=' * 50)
    print('\nWizard Options:',
          '\n1. Full Setup',
          '\n2. DCP Config',
          '\n3. Customer Data File Config'
          '\n4. Set Output Directory'
          )
    
    # User input handler
    selection = int(input('Select setup option (1 to 4): '))
    while selection not in range (4 + 1):
        selection = int(input('Not a valid selection, please select 1 to 4: '))
    if selection == 1:
        print('\nFull Setup:')
        methods.create_config()
    elif selection == 2:
        print('\nUpdate DCP:')
        methods.update_dcp()
    elif selection == 3:
        print('Select new data file:')
        methods.file_explorer()
    else:
        print('Select new output directory:')
        methods.select_directory()

if __name__ == "__main__":
    setup()