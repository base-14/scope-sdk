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

  describe '#get_prompt_version' do
    let(:prompt_id) { 'prompt_123' }

    describe 'defaults to production' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/production",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456', status: 'published')
        )
      end

      it 'fetches production version by default' do
        result = client.get_prompt_version(prompt_id)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(result.status).to eq('published')
        expect(result.production?).to be(true)
      end

      it 'makes request to production endpoint' do
        client.get_prompt_version(prompt_id)

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/production")
      end
    end

    describe 'with production label' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/production",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456', status: 'published')
        )
      end

      it 'fetches production version with explicit label' do
        result = client.get_prompt_version(prompt_id, label: :production)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(result.production?).to be(true)
      end
    end

    describe 'with latest label' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/latest",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456', status: 'draft')
        )
      end

      it 'fetches latest version' do
        result = client.get_prompt_version(prompt_id, label: :latest)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(result.prompt_id).to eq(prompt_id)
        expect(result.status).to eq('draft')
      end

      it 'makes request to latest endpoint' do
        client.get_prompt_version(prompt_id, label: :latest)

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/latest")
      end

      it 'works with string label' do
        client.get_prompt_version(prompt_id, label: 'latest')

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/latest")
      end
    end

    describe 'with specific version' do
      let(:version_id) { 'ver_456' }

      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/versions/#{version_id}",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: version_id, version: 2)
        )
      end

      it 'fetches specific version' do
        result = client.get_prompt_version(prompt_id, version: version_id)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(result.version_id).to eq(version_id)
        expect(result.version).to eq(2)
      end

      it 'makes request to versions endpoint' do
        client.get_prompt_version(prompt_id, version: version_id)

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/versions/#{version_id}")
      end
    end

    describe 'when production version does not exist' do
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
          client.get_prompt_version(prompt_id)
        end.to raise_error(ScopeClient::NoProductionVersionError, /#{prompt_id}/)
      end
    end

    describe 'when latest version does not exist' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/latest",
          response_body: { 'code' => 'not_found', 'message' => 'Not found' },
          status: 404
        )
      end

      it 'raises NotFoundError (not NoProductionVersionError)' do
        expect do
          client.get_prompt_version(prompt_id, label: :latest)
        end.to raise_error(ScopeClient::NotFoundError)
      end
    end

    describe 'caching' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_id}/production",
          response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456')
        )
      end

      it 'caches responses' do
        client.get_prompt_version(prompt_id)
        client.get_prompt_version(prompt_id)

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/production").once
      end

      it 'bypasses cache when disabled' do
        client.get_prompt_version(prompt_id, cache: false)
        client.get_prompt_version(prompt_id, cache: false)

        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/production").twice
      end
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

      result = client.render_prompt(prompt_id, { name: 'Bob' }, label: :latest)

      expect(result).to eq('Hello Bob!')
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
      stub_scope_api(
        :get,
        "/prompts/#{prompt_id}/production",
        response_body: prompt_version_response(prompt_id: prompt_id, version_id: 'ver_456')
      )
    end

    it 'clears all cached data' do
      client.get_prompt_version(prompt_id)
      client.clear_cache
      client.get_prompt_version(prompt_id)

      expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_id}/production").twice
    end
  end

  describe 'fetching prompts by name' do
    let(:prompt_name) { 'my-greeting-prompt' }

    describe '#get_prompt_version with latest label' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_name}/latest",
          response_body: prompt_version_response(prompt_id: 'prompt_123', version_id: 'ver_456', status: 'draft')
        )
      end

      it 'fetches latest version by prompt name' do
        result = client.get_prompt_version(prompt_name, label: :latest)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_name}/latest")
      end
    end

    describe '#get_prompt_version defaults to production' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_name}/production",
          response_body: prompt_version_response(prompt_id: 'prompt_123', version_id: 'ver_456', status: 'published')
        )
      end

      it 'fetches production version by prompt name' do
        result = client.get_prompt_version(prompt_name)

        expect(result).to be_a(ScopeClient::Resources::PromptVersion)
        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_name}/production")
      end
    end

    describe '#render_prompt' do
      before do
        stub_scope_api(
          :get,
          "/prompts/#{prompt_name}/production",
          response_body: prompt_version_response(
            prompt_id: 'prompt_123',
            version_id: 'ver_456',
            content: 'Hello {{name}}, welcome to {{place}}!'
          )
        )
      end

      it 'renders prompt by name' do
        result = client.render_prompt(prompt_name, { name: 'Alice', place: 'Scope' })

        expect(result).to eq('Hello Alice, welcome to Scope!')
        expect(WebMock).to have_requested(:get, "https://api.scope.io/api/v1/prompts/#{prompt_name}/production")
      end
    end
  end
end
