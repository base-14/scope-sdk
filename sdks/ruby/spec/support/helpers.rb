# frozen_string_literal: true

module TestHelpers
  def stub_scope_api(method, path, response_body:, status: 200)
    stub_request(method, "https://api.scope.io/api/v1#{path}")
      .to_return(
        status: status,
        body: response_body.to_json,
        headers: { 'Content-Type' => 'application/json' }
      )
  end

  def prompt_response(prompt_id:, name: 'Test Prompt', description: nil, tags: [])
    {
      'prompt_id' => prompt_id,
      'name' => name,
      'description' => description,
      'latest_version' => 'v3',
      'production_version' => 'v2',
      'tags' => tags,
      'created_at' => '2024-01-15T10:00:00Z',
      'updated_at' => '2024-01-20T15:30:00Z',
      'created_by' => 'user_123'
    }
  end

  def prompt_version_response(prompt_id:, version_id:, version: 1, status: 'published', content: 'Hello {{name}}')
    {
      'prompt_id' => prompt_id,
      'version_id' => version_id,
      'name' => 'Test Prompt',
      'version' => version,
      'content' => content,
      'variables' => content.scan(/\{\{(\w+)\}\}/).flatten.uniq,
      'tags' => [],
      'status' => status,
      'created_at' => '2024-01-15T10:00:00Z',
      'created_by' => 'user_123',
      'promoted_at' => status == 'published' ? '2024-01-18T12:00:00Z' : nil,
      'promoted_by' => status == 'published' ? 'user_456' : nil,
      'metadata' => { 'description' => nil }
    }
  end
end

RSpec.configure do |config|
  config.include TestHelpers
end
