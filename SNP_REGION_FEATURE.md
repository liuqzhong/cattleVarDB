# SNP Region Detection Feature

## Overview
This feature adds gene region information to SNP details, showing where in the gene structure a SNP is located (exon, intron, etc.).

## Database Schema

### New Tables

#### `transcripts` Table
Stores transcript information from GTF file:
- `id`: Primary key
- `transcript_id`: Ensembl transcript ID (unique)
- `gene_id`: Ensembl gene ID
- `chrom`: Chromosome
- `start_pos`: Transcript start position
- `end_pos`: Transcript end position
- `strand`: Strand (+ or -)

#### `exons` Table
Stores exon information from GTF file:
- `id`: Primary key
- `transcript_id`: Foreign key to transcripts table
- `chrom`: Chromosome
- `start_pos`: Exon start position
- `end_pos`: Exon end position
- `exon_number`: Exon number within transcript

## API Changes

### SNP Detail Endpoint (`GET /snps/{snp_id}`)
Enhanced to include region information:

```json
{
  "id": 1,
  "snp_id": "rs110000388",
  "chrom": "1",
  "pos": 1077616,
  "ref": "C",
  "alt": "T",
  "nearest_gene": {
    "gene_id": "ENSBTAG00000000003",
    "gene_name": "GPR180",
    "chrom": "1",
    "start_pos": 1049896,
    "end_pos": 1086098,
    "strand": "+",
    "location": "within",
    "distance": 0,
    "region": "exon 3"  // NEW: Region information
  }
}
```

## Region Detection Logic

The `detect_snp_region()` function in [main.py](backend/main.py#L362) determines SNP location:

1. **Exon**: SNP position falls within any exon boundaries
   - Returns: "exon N" where N is the exon number

2. **Intron**: SNP within gene transcript but not in any exon
   - Returns: "intron"

3. **Intergenic**: SNP outside all gene boundaries
   - Returns: null (distance information shown instead)

## Import Scripts

### import_transcripts.py
Imports transcript and exon data from GTF file:

```bash
python backend/import_transcripts.py --file database/reference/Bos_taurus.ARS-UCD1.2.110.gtf.gz
```

**Import Statistics:**
- Total transcripts: 43,984
- Total exons: 433,820
- Source: Ensembl Bos taurus ARS-UCD1.2.110

## Frontend Display

The SNP detail view in [SNPTableView.vue](frontend/src/views/SNPTableView.vue) displays region information with color-coded tags:

- **Green tag**: SNP in exon (e.g., "exon 3")
- **Orange tag**: SNP in intron
- **No tag**: Intergenic SNP (distance shown instead)

## Usage Example

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. Access SNP details:
   ```
   http://localhost:8000/snps/1
   ```

3. View in frontend:
   - Open SNP Database page
   - Click on any SNP to view details
   - Check the "Gene Information" section for region tag

## Implementation Details

### Database Models
- [TranscriptModel](backend/main.py): SQLAlchemy ORM model for transcripts
- [ExonModel](backend/main.py): SQLAlchemy ORM model for exons

### Key Functions
- `detect_snp_region(db, chrom, pos, gene_id)`: Main region detection logic
- `find_nearest_gene(db, chrom, pos)`: Finds nearest gene (already implemented)

## Performance Considerations

- Indexed fields: `transcript_id`, `gene_id`, `chrom`, `start_pos`, `end_pos`
- Query optimization: Uses indexed range queries for exon detection
- Batch import: Processes 5,000 exons per batch during import

## Future Enhancements

Potential improvements:
1. Add UTR (untranslated region) detection
2. Show upstream/downstream distance for intergenic SNPs
3. Add codon position information for exonic SNPs
4. Display amino acid changes for coding SNPs
