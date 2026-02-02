# frozen_string_literal: true

RSpec.describe ScopeClient::Resources::PromptVersion do
  subject(:prompt_version) { described_class.new(data) }

  let(:data) do
    {
      'prompt_id' => 'prompt_123',
      'version_id' => 'ver_456',
      'name' => 'Test Prompt',
      'version' => 2,
      'content' => 'Hello {{name}}, your balance is {{balance}}',
      'variables' => %w[name balance],
      'status' => 'published',
      'prompt_type' => 'text',
      'metadata' => { 'model' => 'gpt-4', 'temperature' => 0.7 },
      'created_at' => '2024-01-15T10:00:00Z'
    }
  end

  describe 'accessors' do
    it 'provides access to prompt_id and version_id' do
      expect(prompt_version.prompt_id).to eq('prompt_123')
      expect(prompt_version.version_id).to eq('ver_456')
    end

    it 'provides access to version number and content' do
      expect(prompt_version.version).to eq(2)
      expect(prompt_version.content).to eq('Hello {{name}}, your balance is {{balance}}')
    end

    it 'provides access to variables and status' do
      expect(prompt_version.variables).to eq(%w[name balance])
      expect(prompt_version.status).to eq('published')
    end
  end

  describe '#render' do
    it 'renders content with provided variables' do
      result = prompt_version.render(name: 'Alice', balance: '$100')

      expect(result).to eq('Hello Alice, your balance is $100')
    end

    it 'raises MissingVariableError for missing variables' do
      expect do
        prompt_version.render(name: 'Alice')
      end.to raise_error(ScopeClient::MissingVariableError, /balance/)
    end
  end

  describe '#type' do
    it 'returns the prompt type from API response' do
      expect(prompt_version.type).to eq('text')
    end

    it 'defaults to text when prompt_type is nil' do
      version = described_class.new(data.merge('prompt_type' => nil))

      expect(version.type).to eq('text')
    end

    it 'defaults to text when prompt_type is missing' do
      data_without_prompt_type = data.reject { |k, _| k == 'prompt_type' }
      version = described_class.new(data_without_prompt_type)

      expect(version.type).to eq('text')
    end

    it 'returns chat when prompt_type is chat' do
      version = described_class.new(data.merge('prompt_type' => 'chat'))

      expect(version.type).to eq('chat')
    end
  end

  describe '#metadata' do
    it 'returns the metadata from API response' do
      expect(prompt_version.metadata).to eq({ 'model' => 'gpt-4', 'temperature' => 0.7 })
    end

    it 'returns empty hash when metadata is nil' do
      version = described_class.new(data.merge('metadata' => nil))

      expect(version.metadata).to eq({})
    end

    it 'returns empty hash when metadata is missing' do
      data_without_metadata = data.reject { |k, _| k == 'metadata' }
      version = described_class.new(data_without_metadata)

      expect(version.metadata).to eq({})
    end
  end

  describe '#get_metadata' do
    it 'returns value for existing key' do
      expect(prompt_version.get_metadata('model')).to eq('gpt-4')
    end

    it 'returns value for symbol key' do
      expect(prompt_version.get_metadata(:model)).to eq('gpt-4')
    end

    it 'returns default when key is missing' do
      expect(prompt_version.get_metadata('unknown', 'default_value')).to eq('default_value')
    end

    it 'returns nil when key is missing and no default' do
      expect(prompt_version.get_metadata('unknown')).to be_nil
    end

    it 'returns falsy values correctly' do
      version = described_class.new(data.merge('metadata' => { 'temperature' => 0, 'stream' => false }))

      expect(version.get_metadata('temperature')).to eq(0)
      expect(version.get_metadata('stream')).to be(false)
    end

    it 'returns nested values' do
      version = described_class.new(data.merge('metadata' => { 'config' => { 'max_tokens' => 1000 } }))

      expect(version.get_metadata('config')).to eq({ 'max_tokens' => 1000 })
    end
  end

  describe '#draft?' do
    it 'returns true for draft status' do
      draft_version = described_class.new(data.merge('status' => 'draft'))

      expect(draft_version.draft?).to be(true)
    end

    it 'returns false for other statuses' do
      expect(prompt_version.draft?).to be(false)
    end
  end

  describe '#published?' do
    it 'returns true for published status' do
      expect(prompt_version.published?).to be(true)
    end

    it 'returns false for other statuses' do
      draft_version = described_class.new(data.merge('status' => 'draft'))

      expect(draft_version.published?).to be(false)
    end
  end

  describe '#archived?' do
    it 'returns true for archived status' do
      archived_version = described_class.new(data.merge('status' => 'archived'))

      expect(archived_version.archived?).to be(true)
    end

    it 'returns false for other statuses' do
      expect(prompt_version.archived?).to be(false)
    end
  end

  describe '#production?' do
    it 'is an alias for published?' do
      expect(prompt_version.production?).to eq(prompt_version.published?)
    end
  end
end
