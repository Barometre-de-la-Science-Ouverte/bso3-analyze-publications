import re
from bs4 import BeautifulSoup
from project.server.main.logger import get_logger

logger = get_logger(__name__)

def json_grobid(filename, GROBID_VERSIONS):
    try:
        grobid = BeautifulSoup(open(filename, 'r'), 'lxml')
        version = grobid.find('application', {'ident': 'GROBID'}).attrs['version']
        if version not in GROBID_VERSIONS:
            return {}
        return parse_grobid(grobid)
    except:
        logger.debug(f'error with grobid {filename}')
        return {}


def parse_grobid(grobid):
    
    res = {}
    
    #doi_elt = grobid.find('idno', {'type': 'DOI'})
    #if doi_elt:
    #    res['doi'] = doi_elt.get_text('').strip().lower()
    
    authors, affiliations = [], []
    
    source_elt = grobid.find('sourcedesc')
    if source_elt:
        for a in source_elt.find_all('author'):
            author = parse_author(a)
            if author:
                authors.append(author)
                for aff in author.get('affiliations', []):
                    if aff not in affiliations:
                        affiliations.append(aff)
    if authors:
        res['authors'] = authors
    if affiliations:
        res['affiliations'] = affiliations
        
    keywords, abstract = [], []
    profile_elt = grobid.find('profiledesc')
    if profile_elt:
        keywords_elt = profile_elt.find('keywords')
        if keywords_elt:
            for k in keywords_elt.find_all('term'):
                keywords.append({'keyword': k.get_text().strip()})
        abstract_elt = profile_elt.find('abstract')
        if abstract_elt:
            abstract.append({'abstract': abstract_elt.get_text(' ').strip()})
    if keywords:
        res['keywords'] = keywords
    if abstract:
        res['abstract'] = abstract
        
    acknowledgement_elt = grobid.find('div',{'type': 'acknowledgement'})
    if acknowledgement_elt:
        res['acknowledgments'] = [{'acknowledgments': acknowledgement_elt.get_text(' ').strip()}]
        
    references=[]
    ref_elt = grobid.find('div', {'type': 'references'})
    if ref_elt:
        for ref in ref_elt.find_all('biblstruct'):
            #reference = {'reference': ref.get_text(' ').replace('\n',' ').strip()}
            reference = {}
            doi_elt = ref.find('idno', {'type': 'DOI'})
            if doi_elt:
                reference['doi'] = doi_elt.get_text(' ').lower().strip()
                references.append(reference)
    if references:
        res['references'] = references

    res['has_availability_statement'] = False
        
    return res
    
def parse_author(author):
    res = {}
    first_name_elt = author.find('forename')
    if first_name_elt:
        res['first_name'] = first_name_elt.get_text(' ').strip()
    last_name_elt = author.find('surname')
    if last_name_elt:
        res['last_name'] = last_name_elt.get_text(' ').strip()
    email_elt = author.find('email')
    if email_elt:
        res['email'] = email_elt.get_text(' ').strip()
    orcid_elt = author.find('idno', {'type': 'ORCID'})
    if orcid_elt:
        res['orcid'] = orcid_elt.get_text(' ').strip()
    affiliations = []
    for affiliation_elt in author.find_all('affiliation'):
        aff_name = affiliation_elt.get_text(' ').replace('\n', ' ')
        aff_name = re.sub(' +', ' ', aff_name).strip()
        affiliation = {'name': aff_name}
        orgs = []
        for org_elt in affiliation_elt.find_all('orgname'):
            orgs.append({'name': org_elt.get_text(' ').strip()})
        if orgs:
            affiliation['orgs'] = orgs

        address_elt = affiliation_elt.find('addrline')
        if address_elt:
            affiliation['address'] = address_elt.get_text(' ').strip()

        city_elt = affiliation_elt.find('settlement')
        if city_elt:
            affiliation['city'] = city_elt.get_text(' ').strip()

        zip_elt = affiliation_elt.find('postcode')
        if zip_elt:
            affiliation['zipcode'] = zip_elt.get_text(' ').strip()
        
        country_elt = affiliation_elt.find('country')
        if country_elt:
            affiliation['country'] = country_elt.get_text(' ').strip()


        affiliations.append(affiliation)

    if affiliations:
        res['affiliations'] = affiliations
    return res   
