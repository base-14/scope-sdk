# frozen_string_literal: true

RSpec.describe ScopeClient::Renderer do
  describe '#render' do
    it 'replaces variables with values' do
      renderer = described_class.new('Hello {{name}}, welcome to {{place}}!', %w[name place])
      result = renderer.render(name: 'Alice', place: 'Scope')

      expect(result).to eq('Hello Alice, welcome to Scope!')
    end

    it 'handles multiple occurrences of the same variable' do
      renderer = described_class.new('{{name}} said: Hello {{name}}!', ['name'])
      result = renderer.render(name: 'Bob')

      expect(result).to eq('Bob said: Hello Bob!')
    end

    it 'converts non-string values to strings' do
      renderer = described_class.new('Count: {{count}}', ['count'])
      result = renderer.render(count: 42)

      expect(result).to eq('Count: 42')
    end

    it 'raises MissingVariableError for unrendered variables' do
      renderer = described_class.new('Hello {{name}}, your balance is {{balance}}', %w[name balance])

      expect do
        renderer.render(name: 'Alice')
      end.to raise_error(ScopeClient::MissingVariableError, /balance/)
    end

    it 'raises ValidationError for unknown variables' do
      renderer = described_class.new('Hello {{name}}', ['name'])

      expect do
        renderer.render(name: 'Alice', unknown: 'value')
      end.to raise_error(ScopeClient::ValidationError, /unknown/)
    end

    it 'works with empty variables list' do
      renderer = described_class.new('No variables here', [])
      result = renderer.render({})

      expect(result).to eq('No variables here')
    end

    it 'handles string keys in values hash' do
      renderer = described_class.new('Hello {{name}}!', ['name'])
      result = renderer.render('name' => 'Charlie')

      expect(result).to eq('Hello Charlie!')
    end
  end

  describe '#extract_variables' do
    it 'extracts all variable names from content' do
      renderer = described_class.new('Hello {{name}}, your {{item}} costs {{price}}', [])

      expect(renderer.extract_variables).to contain_exactly('name', 'item', 'price')
    end

    it 'returns unique variable names' do
      renderer = described_class.new('{{name}} and {{name}} again', [])

      expect(renderer.extract_variables).to eq(['name'])
    end

    it 'returns empty array when no variables' do
      renderer = described_class.new('No variables', [])

      expect(renderer.extract_variables).to eq([])
    end
  end
end
