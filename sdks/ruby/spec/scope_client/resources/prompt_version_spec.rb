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
