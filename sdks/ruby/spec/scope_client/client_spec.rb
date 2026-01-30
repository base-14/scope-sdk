# frozen_string_literal: true

RSpec.describe ScopeClient::Client do
  subject(:client) { described_class.new }

  describe '#initialize' do
    it 'creates client with default configuration' do
      expect(client.config.credentials.api_key).to eq('test_api_key_12345')
    end

    it 'raises ConfigurationError when credentials is nil' do
      ScopeClient.configure { |c| c.credentials = nil }

      expect { described_class.new }.to raise_error(ScopeClient::ConfigurationError, /credentials is required/)
    end

    it 'raises ConfigurationError when api_key is nil' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: 'test_org',
        api_key: nil,
        api_secret: 'test_secret'
      )
      ScopeClient.configure { |c| c.credentials = credentials }

      expect { described_class.new }.to raise_error(ScopeClient::ConfigurationError, /api_key is required/)
    end

    it 'raises ConfigurationError when api_key is empty' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: 'test_org',
        api_key: '',
        api_secret: 'test_secret'
      )
      ScopeClient.configure { |c| c.credentials = credentials }

      expect { described_class.new }.to raise_error(ScopeClient::ConfigurationError, /api_key is required/)
    end

    it 'raises ConfigurationError when org_id is nil' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: nil,
        api_key: 'test_key',
        api_secret: 'test_secret'
      )
      ScopeClient.configure { |c| c.credentials = credentials }

      expect { described_class.new }.to raise_error(ScopeClient::ConfigurationError, /org_id is required/)
    end

    it 'raises ConfigurationError when api_secret is nil' do
      credentials = ScopeClient::Credentials::ApiKey.new(
        org_id: 'test_org',
        api_key: 'test_key',
        api_secret: nil
      )
      ScopeClient.configure { |c| c.credentials = credentials }

      expect { described_class.new }.to raise_error(ScopeClient::ConfigurationError, /api_secret is required/)
    end

    it 'merges custom options with global config' do
      custom_client = described_class.new(timeout: 60)

      expect(custom_client.config.timeout).to eq(60)
    end

    it 'creates cache when cache_enabled is true' do
      expect(client.cache).to be_a(ScopeClient::Cache)
    end

    it 'does not create cache when cache_enabled is false' do
      no_cache_client = described_class.new(cache_enabled: false)

      expect(no_cache_client.cache).to be_nil
    end
  end

  describe '#get_prompt' do
    let(:prompt_id) { 'prompt_123' }

    before do
      stub_scope_api(:get, "/prompts/#{prompt_id}", response_body: prompt_response(prompt_id: prompt_id))
    end

    it 'fetches and returns the prompt' do
      result = client.get_prompt(prompt_id)

      expect(result).to be_a(ScopeClient::Resources::Prompt)
      expect(result.prompt_id).to eq(prompt_id)
    end

    it 'caches the result' do
      client.get_prompt(prompt_id)
      client.get_prompt(prompt_id)

      expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}").once
    end

    it 'skips cache when cache: false' do
      client.get_prompt(prompt_id)
      client.get_prompt(prompt_id, cache: false)

      expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}").twice
    end
  end

  describe '#get_prompt_latest' do
    let(:prompt_id) { 'prompt_123' }

    before do
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/latest",
        response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456', status: 'draft')
      )
    end

    it 'fetches and returns the latest prompt version' do
      result = client.get_prompt_latest(prompt_id)

      expect(result).to be_a(ScopeClient::Resources::PromptVersion)
      expect(result.prompt_id).to eq(prompt_id)
      expect(result.status).to eq('draft')
    end
  end

  describe '#get_prompt_production' do
    let(:prompt_id) { 'prompt_123' }

    context 'when production version exists' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/production",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456', status: 'published')
        )
      end

      it 'fetches and returns the production prompt version' do
        result = client.get_prompt_production(prompt_id)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(result.status).to eq('published')
        expect(result.production?).to be(true)
      end
    end

    context 'when production version does not exist' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/production",
          response_body: { 'code' => 'not_found', 'message' => 'Not found' },
          status: 404
        )
      end

      it 'raises NoProductionVersionError' do
        expect do
          client.get_prompt_production(prompt_id)
        end.to raise_error(ScopeClient::NoProductionVersionError, /#{prompt_id}/)
      end
    end
  end

  describe '#get_prompt_version' do
    let(:prompt_id) { 'prompt_123' }
    let(:version_id) { 'ver_456' }

    before do
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/versions/#{version_id}",
        response_body: prompt_version_response(prompt_id: prompt_id, version_id: version_id, version: 2)
      )
    end

    it 'fetches and returns the specific prompt version' do
      result = client.get_prompt_version(prompt_id, version_id)

      expect(result).to be_a(ScopeClient::Resources::PromptVersion)
      expect(result.version_id).to eq(version_id)
      expect(result.version).to eq(2)
    end
  end

  describe '#list_prompts' do
    before do
      stub_scope_api(
        :get,
        '/prompts',
        response_body: {
          'data' => [
            prompt_response(prompt_id: 'prompt_1', name: 'Prompt 1'),
            prompt_response(prompt_id: 'prompt_2', name: 'Prompt 2')
          ],
          'meta' => { 'next_cursor' => nil, 'has_more' => false }
        }
      )
    end

    it 'returns paginated list of prompts' do
      result = client.list_prompts

      expect(result[:data]).to be_an(Array)
      expect(result[:data].length).to eq(2)
      expect(result[:data].first).to be_a(ScopeClient::Resources::Prompt)
      expect(result[:meta]['has_more']).to be(false)
    end
  end

  describe '#render_prompt' do
    let(:prompt_id) { 'prompt_123' }

    before do
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/production",
        response_body: prompt_version_response(
          prompt_id: prompt_id,
          version_id: 'ver_456',
          content: 'Hello {{name}}, welcome to {{place}}!'
        )
      )
    end

    it 'renders prompt with variable substitution' do
      result = client.render_prompt(prompt_id, { name: 'Alice', place: 'Scope' })

      expect(result).to eq('Hello Alice, welcome to Scope!')
    end

    it 'uses production version by default' do
      client.render_prompt(prompt_id, { name: 'Alice', place: 'Scope' })

      expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/production")
    end

    it 'uses latest version when specified' do
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/latest",
        response_body: prompt_version_response(
          prompt_id: prompt_id,
          version_id: 'ver_789',
          content: 'Hello {{name}}!'
        )
      )

      result = client.render_prompt(prompt_id, { name: 'Bob' }, version: :latest)

      expect(result).to eq('Hello Bob!')
    end

    it 'uses specific version when version_id provided' do
      version_id = 'ver_specific'
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/versions/#{version_id}",
        response_body: prompt_version_response(
          prompt_id: prompt_id,
          version_id: version_id,
          content: 'Specific: {{name}}'
        )
      )

      result = client.render_prompt(prompt_id, { name: 'Charlie' }, version: version_id)

      expect(result).to eq('Specific: Charlie')
    end

    it 'raises MissingVariableError for missing variables' do
      expect do
        client.render_prompt(prompt_id, { name: 'Alice' })
      end.to raise_error(ScopeClient::MissingVariableError, /place/)
    end
  end

  describe '#clear_cache' do
    let(:prompt_id) { 'prompt_123' }

    before do
      stub_scope_api(:get, "/prompts/#{prompt_id}", response_body: prompt_response(prompt_id: prompt_id))
    end

    it 'clears all cached data' do
      client.get_prompt(prompt_id)
      client.clear_cache
      client.get_prompt(prompt_id)

      expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}").twice
    end
  end
end
