import { describe, expect, it } from 'vitest'
import { fileLabel } from './knowledge'

describe('fileLabel', () => {
  it('strips content/ prefix and .md suffix', () => {
    expect(fileLabel('content/cloud-basics.md')).toBe('cloud-basics')
  })

  it('strips yaml/yml suffix for machine-readable files', () => {
    expect(fileLabel('checklist.yaml')).toBe('checklist')
    expect(fileLabel('content/x.yml')).toBe('x')
  })

  it('labels SKILL.md explicitly so it reads as the pack intro', () => {
    expect(fileLabel('SKILL.md')).toBe('说明 · SKILL.md')
  })

  it('leaves unknown paths untouched apart from known suffixes', () => {
    expect(fileLabel('notes.txt')).toBe('notes.txt')
  })
})
