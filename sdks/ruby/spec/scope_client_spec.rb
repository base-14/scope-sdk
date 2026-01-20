# frozen_string_literal: true

RSpec.describe ScopeClient do
  describe '.configure' do
    it 'yields the configuration' do
      described_class.configure do |config|
        config.api_key = 'custom_key'
        config.timeout = 60
      end

      expect(described_class.configuration.api_key).to eq('custom_key')
      expect(described_class.configuration.timeout).to eq(60)
    end
  end

  describe '.client' do
    it 'creates a new client instance' do
      client = described_class.client

      expect(client).to be_a(ScopeClient::Client)
    end

    it 'passes options to the client' do
      client = described_class.client(timeout: 120)

      expect(client.config.timeout).to eq(120)
    end
  end

  describe '.reset_configuration!' do
    it 'resets to default configuration' do
      described_class.configure do |config|
        config.timeout = 999
      end

      described_class.reset_configuration!

      expect(described_class.configuration.timeout).to eq(30)
    end
  end

  describe 'VERSION' do
    it 'has a version number' do
      expect(ScopeClient::VERSION).not_to be_nil
      expect(ScopeClient::VERSION).to match(/\d+\.\d+\.\d+/)
    end
  end
end
