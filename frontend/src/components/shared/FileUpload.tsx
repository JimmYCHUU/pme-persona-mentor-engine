import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '../../api/client'

export function FileUpload({ personaId }: { personaId: string }) {
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      for (const file of acceptedFiles) {
        await api.uploadVault(file, personaId)
      }
    },
    [personaId],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'video/mp4': ['.mp4'],
      'audio/mpeg': ['.mp3'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  })

  return (
    <div {...getRootProps()} style={{ border: '1px dashed var(--accent)', padding: 12, borderRadius: 8 }}>
      <input {...getInputProps()} />
      {isDragActive ? 'Drop files…' : 'Upload PDF, MP4, MP3, DOCX'}
    </div>
  )
}
